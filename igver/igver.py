import os
import subprocess
import uuid
import time

from PIL import Image
import matplotlib.pyplot as plt
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


def is_running_in_container():
    """Detect if running inside a container (Docker or Singularity)"""
    # Check environment variable first
    if os.environ.get('IGVER_IN_CONTAINER', '').strip() == '1':
        return True
    if os.environ.get('IGVER_NO_SINGULARITY', '').strip() == '1':
        return True
    
    # Check for Docker
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check for Singularity
    if os.environ.get('SINGULARITY_CONTAINER'):
        return True
    
    # Check cgroup for docker/lxc
    try:
        with open('/proc/1/cgroup', 'r') as f:
            content = f.read()
            if 'docker' in content or 'lxc' in content:
                return True
    except:
        pass
    
    return False


def _get_figures(png_paths, remove_png, dpi, debug):
    figures = []
    for png_path in png_paths:
        image = Image.open(png_path)
        width, height = image.size  # Get original image dimensions

        # Convert to inches for Matplotlib
        figsize = (width / dpi, height / dpi)

        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.imshow(image)
        ax.axis("off")

        figures.append(fig)

        # Remove the temp PNG if requested
        if remove_png:
            os.remove(png_path)
            if debug:
                print(f"[LOG:{time.ctime()}] Removed image {png_path}")
    
    return figures


def _convert_svg_to_pdf(svg_paths, remove_svg, dpi, debug):
    """Convert SVG files to PDF format"""
    if not HAS_CAIROSVG:
        raise ImportError("cairosvg is required for PDF output. Install with: pip install cairosvg")
    
    pdf_paths = []
    for svg_path in svg_paths:
        pdf_path = svg_path.replace('.svg', '.pdf')
        
        # Convert SVG to PDF
        cairosvg.svg2pdf(url=svg_path, write_to=pdf_path, dpi=dpi)
        pdf_paths.append(pdf_path)
        
        if debug:
            print(f"[LOG:{time.ctime()}] Converted {svg_path} to {pdf_path}")
        
        # Remove SVG if requested
        if remove_svg:
            os.remove(svg_path)
            if debug:
                print(f"[LOG:{time.ctime()}] Removed SVG file {svg_path}")
    
    return pdf_paths


def load_screenshots(paths, regions, output_dir='/tmp', genome="hg19", igv_dir="/opt/IGV_2.19.5", 
                     overwrite=True, remove_png=True, dpi=300,
                     singularity_image='docker://sahuno/igver:latest', singularity_args='-B /home',
                     debug=False, output_format='png', use_singularity=None, **kwargs):
    """
    Generates IGV screenshots and loads them into a Matplotlib figure.

    Parameters:
        paths (list of str): Paths to input files (BAM, BEDPE, VCF, bigWig, etc).
        regions (list of str): List of genomic regions in 'chr:start-end' format.
        output_dir (str, optional): Directory for output screenshots (default: "/tmp").
        genome (str, optional): Genome version (default: "hg19").
        igv_dir (str, optional): Directory containing IGV installation (default: "/opt/IGV_2.19.5").
        overwrite (bool, optional): Whether to overwrite existing PNG files (default: True).
        remove_png (bool, optional): Whether to remove created PNG files (default: True).
        dpi (int, optional): DPI of the figure (default: 300).
        singularity_image (str, optional): singularity image path (default: "docker://sahuno/igver:latest").
        singularity_args (str, optional): singularity arguments string (default: "-B /home").
        debug (bool, optional): Whether to show logs for debugging (default: False).
        output_format (str, optional): Output image format - 'png', 'svg', or 'pdf' (default: 'png').
        **kwargs (optional): *kwargs* such as tag, max_panel_height, overlap_display, igv_config for create_batch_script

    Returns:
        list of matplotlib.figure.Figure: list of figures containing the IGV screenshots.
    """
    from .igver import create_batch_script, run_igv  # Import helper functions

    # Create batch script and expected PNG paths
    tmpdir = os.getenv("TMPDIR", output_dir)  # Default to /tmp if TMPDIR is not set
    if output_dir == '/tmp':
        output_dir = os.environ['TMPDIR']
    if debug:
        print(f"[LOG:{time.ctime()}] TMPDIR is set to: {tmpdir}")
    # Pass output_format to create_batch_script
    batch_script, output_paths = create_batch_script(paths, regions, output_dir, genome, 
                                                     output_format=output_format, **kwargs)
    for path in paths:
        abspath = os.path.abspath(path)
        realpath = os.path.realpath(path)
        bam_dir_abs = os.path.split(abspath)[0]
        bam_dir_real = os.path.split(realpath)[0]
        singularity_args += f' -B {bam_dir_abs}'
        if bam_dir_abs != bam_dir_real:
            singularity_args += f' -B {bam_dir_real}'
    singularity_args += f' -B {os.path.realpath(output_dir)}'
    singularity_args += f' -B {tmpdir}'

    # Run IGV to generate the screenshots
    singularity_image = os.environ.get('IGVER_IMAGE', singularity_image)
    run_igv(batch_script, output_paths, igv_dir, overwrite, 
        singularity_image=singularity_image, singularity_args=singularity_args, 
        debug=debug, use_singularity=use_singularity)

    # Check if screenshots were generated
    if not output_paths:
        raise RuntimeError("[ERROR] No screenshots generated.")

    # Handle different output formats
    if output_format == 'pdf':
        # For PDF, we need to convert from SVG
        figures = _convert_svg_to_pdf(output_paths, remove_png, dpi, debug)
    elif output_format == 'svg':
        # For SVG, return the paths as figures are not needed
        figures = output_paths  # Return paths instead of matplotlib figures
    else:
        # Load PNG screenshots into Matplotlib figures
        figures = _get_figures(output_paths, remove_png, dpi, debug)

    return figures


def _parse_bed_file(bed_file, output_dir, overlap_display='squish', max_panel_height=200, additional_pref=None, tag=None, output_format='png'):
    """
    Parse BED format file (BED3 or BED6) to extract regions
    BED3: chrom, chromStart, chromEnd
    BED6: chrom, chromStart, chromEnd, name, score, strand
    """
    png_paths = []
    region_content = []
    
    with open(bed_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('track') or line.startswith('browser'):
                continue
                
            fields = line.split('\t')
            if len(fields) < 3:
                continue
                
            chrom = fields[0]
            start = fields[1]
            end = fields[2]
            
            # Handle optional name field from BED6
            region_name = ''
            if len(fields) >= 4 and fields[3]:
                region_name = fields[3]
            
            # Format region string
            region = f"{chrom}:{start}-{end}"
            region_tag = region.replace(':', '-')
            
            # Create filename with appropriate extension
            ext = 'svg' if output_format in ['svg', 'pdf'] else output_format
            if region_name:
                png_fname = f"{region_tag}.{region_name}.{ext}"
            elif tag:
                png_fname = f"{region_tag}.{tag}.{ext}"
            else:
                png_fname = f"{region_tag}.{ext}"
                
            png_path = os.path.join(output_dir, png_fname)
            png_paths.append(png_path)
            
            # Create batch content
            region_content.append(f'goto {region}')
            if overlap_display != 'expand':
                region_content.append(overlap_display)
            region_content.append(f'maxPanelHeight {max_panel_height}')
            if additional_pref:
                region_content.append(additional_pref)
            region_content.append(f'snapshot {png_fname}')
    
    return png_paths, region_content


def _parse_region_file(region_file, output_dir, overlap_display='squish', max_panel_height=200, additional_pref=None, tag=None, output_format='png'):
    """
    Parse region and tag from line (legacy text format)
    """
    png_paths = []
    region_content = []
    for line in open(region_file):
        out_tag = ''
        sv_tag = ''
        field = line.strip().split() # split by either ' ' or '\t'
        region = []
        region_tags = []
        for item in field:
            is_region = (item.count(':')==1 and item.count('-')==1)
            if is_region:
                region_tag = item.replace(':', '-')
                region_tags.append(region_tag)
                region.append(item)
            else:
                sv_tag = item
        out_tag = '.'.join(region_tags)
        region = ' '.join(region)
        if sv_tag:
            out_tag += f'.{sv_tag}' # e.g. ins, del, translocation, ...
        ext = 'svg' if output_format in ['svg', 'pdf'] else output_format
        png_fname = out_tag + f'.{ext}'
        png_path = os.path.join(output_dir, png_fname)
        png_paths.append(png_path)
        
        region_content.append(f'goto {region}')
        if overlap_display != 'expand':
            region_content.append(overlap_display)
        region_content.append(f'maxPanelHeight {max_panel_height}')
        if additional_pref:
            region_content.append(additional_pref)
        region_content.append(f'snapshot {png_fname}')

    return png_paths, region_content


def _parse_region_string(region, output_dir, overlap_display='squish', max_panel_height=200, additional_pref=None, tag=None, output_format='png'):
    """
    Parse region and tag from cli argument
    """
    region_content = []
    region_tag = region.replace(':', '-').replace(' ', '.')
    ext = 'svg' if output_format in ['svg', 'pdf'] else output_format
    png_fname = f"{region_tag}.{ext}"
    if tag:
        png_fname = f"{region_tag}.{tag}.{ext}"
    png_path = os.path.join(output_dir, png_fname)
    
    region_content.append(f'goto {region}')
    if overlap_display != 'expand':
        region_content.append(overlap_display)
    region_content.append(f'maxPanelHeight {max_panel_height}')
    if additional_pref:
        region_content.append(additional_pref)
    region_content.append(f'snapshot {png_fname}')

    png_paths = [png_path]

    return png_paths, region_content


def create_batch_script(paths, regions, output_dir, genome='hg19', tag=None, max_panel_height=200,
                        overlap_display='squish', igv_config=None, output_format='png'):
    """
    Creates an IGV batch script to generate screenshots for the given BAM files and regions.
    
    Parameters:
        paths (list of str): Paths to BAM files.
        regions (list of str): List of regions in 'chr:start-end' format.
        output_dir (str): Directory where screenshots will be saved.
        genome (str, optional): Genome version (default: 'hg19').
        tag (str, optional): Tag to suffix the PNG file name (default: None).
        max_panel_height (int, optional): Maximum panel height for IGV (default: 200).
        overlap_display (str, optional): Display mode for overlapping reads ('expand', 'collapse', 'squish', default: 'squish').
        igv_config (str, optional): Path to additional IGV preferences file (default: None).

    Returns:
        str: The path to the generated IGV batch script.
    """
    assert overlap_display in ['expand', 'collapse', 'squish'], f"Invalid overlap_display: {overlap_display}"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Generate a unique batch file name
    batch_filename = os.path.join(output_dir, f'{uuid.uuid4()}.batch')
    
    # Read additional IGV preferences if provided
    additional_pref = ""
    if igv_config and os.path.exists(igv_config):
        with open(igv_config, 'r') as f:
            additional_pref = f.read().strip()

    # Create batch file content
    batch_content = [
        'new',
        f'snapshotDirectory {output_dir}',
        f'genome {genome}'
    ]
    for bam in paths:
        batch_content.append(f'load {bam}')
    
    png_paths, region_content = _get_paths_and_regions(regions, 
        output_dir=output_dir, overlap_display=overlap_display, 
        max_panel_height=max_panel_height, additional_pref=additional_pref, tag=tag,
        output_format=output_format)
    batch_content += region_content
    batch_content.append('exit')
    batch_text = '\n'.join(batch_content)
    
    # Write to batch file
    with open(batch_filename, 'w') as batch_file:
        batch_file.write(batch_text)
    
    return batch_filename, png_paths


def _get_paths_and_regions(regions, **kwargs):
    png_paths = []
    region_content = []
    for region in regions:
        if os.path.exists(region): # input is region file
            # Check if it's a BED file based on extension
            if region.endswith('.bed'):
                _png_paths, _region_content = _parse_bed_file(region, **kwargs)
            else:
                # Assume it's a text file with custom format
                _png_paths, _region_content = _parse_region_file(region, **kwargs)

        else: # input is region argument(s)
            _png_paths, _region_content = _parse_region_string(region, **kwargs)
        png_paths += _png_paths
        region_content += _region_content
    
    return png_paths, region_content


def _remove_previous_output(png_paths, debug=False):
    for png_path in png_paths:
        if os.path.exists(png_path):
            os.remove(png_path)
            if debug:
                print(f"[LOG:{time.ctime()}] Removed existing {png_path}")


def run_igv(batch_script, png_paths, igv_dir="/opt/IGV_2.19.5", overwrite=False, 
            singularity_image='docker://sahuno/igver:latest', singularity_args='-B /data1 -B /home',
            debug=False, use_singularity=None):
    """
    Runs IGV using the generated batch script and ensures all PNG screenshots are created.

    Parameters:
        batch_script (str): Path to the IGV batch script.
        png_paths (list of str): Expected paths of the output PNG screenshot.
        igv_dir (str, optional): Directory containing IGV installation (default: "/opt/IGV_2.19.5").
        overwrite (bool, optional): Whether to overwrite existing PNG files (default: False).
        debug (bool, optional): Whether to show logs for debugging (default: False).

    Returns:
        list of str: Paths to the generated PNG files.
    """
    # Auto-detect if we should use singularity
    if use_singularity is None:
        use_singularity = not is_running_in_container()
    
    # assert os.path.exists(igv_dir), f"[ERROR:{time.ctime()}] {igv_dir} does not exist"
    igv_runfile = os.path.join(igv_dir, "igv.sh")
    # assert os.path.exists(igv_runfile), f"[ERROR:{time.ctime()}] {igv_runfile} does not exist"

    # IGV command
    cmd = f'xvfb-run --auto-display --server-args="-screen 0 1920x1080x24" {igv_runfile} -b {batch_script} --igvDirectory {igv_dir}'
    
    # Only wrap with singularity if needed
    if use_singularity:
        cmd = f'singularity run {singularity_args} {singularity_image} {cmd}'
        if debug:
            print(f"[LOG:{time.ctime()}] Running IGV with Singularity")
    else:
        if debug:
            print(f"[LOG:{time.ctime()}] Running IGV directly (container mode)")
    
    if debug:
        print(f"[LOG:{time.ctime()}] Running IGV command:\n{cmd}")

    # If overwrite is enabled, remove existing PNG files
    if overwrite:
        _remove_previous_output(png_paths, debug)

    # Run IGV
    n_iter = 0
    max_iter = 2
    while not all(os.path.exists(png) for png in png_paths) and n_iter < max_iter:
        if debug:
            print(f"[LOG:{time.ctime()}] Iteration #{n_iter + 1}: Ensuring PNG files exist")
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Print STDOUT and STDERR if debug=True
        if debug:
            print(f"[STDOUT:{time.ctime()}]\n{result.stdout.decode()}")
            print(f"[STDERR:{time.ctime()}]\n{result.stderr.decode()}")
        n_iter += 1

    if not all(os.path.exists(png) for png in png_paths):
        raise RuntimeError(f"[ERROR:{time.ctime()}] Failed to generate all PNG files after {max_iter} iterations.")

    # Cleanup batch script
    os.remove(batch_script)
    if debug:
        print(f"[LOG:{time.ctime()}] Removed batch script {batch_script}")

    return png_paths
