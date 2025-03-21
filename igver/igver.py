import os
import subprocess
import uuid
import time

from PIL import Image
import matplotlib.pyplot as plt


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


def load_screenshots(paths, regions, output_dir='/tmp', genome="hg19", igv_dir="/opt/IGV_2.17.4", 
                     overwrite=True, remove_png=True, dpi=300,
                     singularity_image='docker://quay.io/soymintc/igver', singularity_args='-B /home',
                     debug=False, **kwargs):
    """
    Generates IGV screenshots and loads them into a Matplotlib figure.

    Parameters:
        paths (list of str): Paths to input files (BAM, BEDPE, VCF, bigWig, etc).
        regions (list of str): List of genomic regions in 'chr:start-end' format.
        output_dir (str, optional): Directory for output screenshots (default: "/tmp").
        genome (str, optional): Genome version (default: "hg19").
        igv_dir (str, optional): Directory containing IGV installation (default: "/opt/IGV_2.17.4").
        overwrite (bool, optional): Whether to overwrite existing PNG files (default: True).
        remove_png (bool, optional): Whether to remove created PNG files (default: True).
        dpi (int, optional): DPI of the figure (default: 300).
        singularity_image (str, optional): singularity image path (default: "docker://quay.io/soymintc/igver").
        singularity_args (str, optional): singularity arguments string (default: "-B /home").
        debug (bool, optional): Whether to show logs for debugging (default: False).
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
    batch_script, png_paths = create_batch_script(paths, regions, output_dir, genome, **kwargs)
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
    run_igv(batch_script, png_paths, igv_dir, overwrite, 
        singularity_image=singularity_image, singularity_args=singularity_args, debug=debug)

    # Check if screenshots were generated
    if not png_paths:
        raise RuntimeError("[ERROR] No screenshots generated.")

    # Load each screenshot into a Matplotlib figure with high resolution
    figures = _get_figures(png_paths, remove_png, dpi, debug)

    return figures


def _parse_region_file(region_file, output_dir, overlap_display='squish', max_panel_height=200, additional_pref=None, tag=None):
    """
    Parse region and tag from line
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
        png_fname = out_tag + '.png'
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


def _parse_region_string(region, output_dir, overlap_display='squish', max_panel_height=200, additional_pref=None, tag=None):
    """
    Parse region and tag from cli argument
    """
    region_content = []
    region_tag = region.replace(':', '-').replace(' ', '.')
    png_fname = f"{region_tag}.png"
    if tag:
        png_fname = f"{region_tag}.{tag}.png"
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
                        overlap_display='squish', igv_config=None):
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
        max_panel_height=max_panel_height, additional_pref=additional_pref, tag=tag)
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


def run_igv(batch_script, png_paths, igv_dir="/opt/IGV_2.17.4", overwrite=False, 
            singularity_image='docker://shahcompbio/igver', singularity_args='-B /data1 -B /home',
            debug=False):
    """
    Runs IGV using the generated batch script and ensures all PNG screenshots are created.

    Parameters:
        batch_script (str): Path to the IGV batch script.
        png_paths (list of str): Expected paths of the output PNG screenshot.
        igv_dir (str, optional): Directory containing IGV installation (default: "/opt/IGV_2.17.4").
        overwrite (bool, optional): Whether to overwrite existing PNG files (default: False).
        debug (bool, optional): Whether to show logs for debugging (default: False).

    Returns:
        list of str: Paths to the generated PNG files.
    """
    # assert os.path.exists(igv_dir), f"[ERROR:{time.ctime()}] {igv_dir} does not exist"
    igv_runfile = os.path.join(igv_dir, "igv.sh")
    # assert os.path.exists(igv_runfile), f"[ERROR:{time.ctime()}] {igv_runfile} does not exist"

    # IGV command
    cmd = f'xvfb-run --auto-display --server-args="-screen 0 1920x1080x24" {igv_runfile} -b {batch_script} --igvDirectory {igv_dir}'
    cmd = f'singularity run {singularity_args} {singularity_image} {cmd}'
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
