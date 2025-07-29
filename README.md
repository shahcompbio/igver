# IGVer

Conveniently take IGV snapshots of multiple BAM files over multiple genomic regions.

**New in v0.2.0:**
- Updated to IGV version 2.19.5 (from 2.17.4)
- Added support for BED format input files (BED3 and BED6)
- Improved region file parsing
- Added support for multiple output formats (PNG, SVG, PDF)

**Container Versions:**
- `sahuno/igver:latest` - Always the most recent version (recommended)
- `sahuno/igver:2.19.5` - Specific version with IGV 2.19.5
- Version tags available starting from 2.19.5

## Table of Contents
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [CLI](#cli)
  - [Python API](#python-api)
- [Supported File Formats](#supported-file-formats)
- [Output File Naming](#output-file-naming)
- [Examples](#examples)
- [Advanced Usage](#advanced-usage)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Authors](#authors)

## Features
- Generate high-resolution IGV screenshots programmatically
- Support for multiple BAM files and multiple genomic regions
- BED file support (BED3 and BED6 formats)
- Run IGV in a containerized environment for reproducibility
- Integrate with Python scripts using the API
- Customize IGV display preferences

## Requirements
- Python 3.7+
- Singularity/Apptainer or Docker
- For local installation: matplotlib, Pillow, PyYAML

## Installation

### Option 1: Using Container (Recommended for HPC)
```bash
# For Singularity/Apptainer
singularity pull docker://sahuno/igver:latest

# For Docker
docker pull sahuno/igver:latest
```

**Note**: Specific versions are available starting from `igver:2.19.5`

### Option 2: Local Installation
```bash
pip install igver
```
**Note**: Local installation still requires Singularity or Docker to run IGV.

## Quick Start

```bash
# Using Singularity (recommended for HPC)
singularity exec docker://sahuno/igver:latest igver.py \
  -i sample.bam -r "chr1:1000000-2000000" -o output/

# Using local installation
igver -i sample.bam -r "chr1:1000000-2000000" -o output/

# Using BED file for regions
igver -i sample.bam -r regions.bed -o output/
```

## Usage

### CLI

#### Basic Usage
```bash
igver \
  -i test/test_tumor.bam test/test_normal.bam \
  -r "chr1:1000000-2000000" \
  -o ./screenshots
```

#### Using BED Files
```bash
# BED3 format (chr, start, end)
igver \
  -i sample.bam \
  -r regions.bed \
  -o ./screenshots

# BED6 format (includes region names in output)
igver \
  -i sample.bam \
  -r regions_with_names.bed \
  -o ./screenshots
```

#### Multiple Regions
```bash
# Multiple regions in one panel
igver \
  -i sample.bam \
  -r "chr1:1000-2000 chr2:3000-4000" \
  -o ./screenshots

# Multiple separate regions
igver \
  -i sample.bam \
  -r "chr1:1000-2000" "chr2:3000-4000" \
  -o ./screenshots
```

#### Command Line Options
```
igver --help

Options:
  -i, --input         Input BAM/BEDPE/VCF/bigWig file(s)
  -r, --regions       Genomic regions or BED file
  -o, --output        Output directory (default: /tmp)
  -g, --genome        Reference genome (default: hg19)
  --dpi               Output resolution (default: 300)
  -p, --max-panel-height   Maximum panel height (default: 200)
  -d, --overlap-display    Display mode: expand/collapse/squish (default: squish)
  -c, --igv-config    Custom IGV preferences file
  -f, --format        Output format: png/svg/pdf (default: png)
  --singularity-image Container image (default: docker://sahuno/igver:latest)
  --debug             Enable debug logging
```

### Python API

#### Basic Example
```python
import igver

# Generate screenshots
figures = igver.load_screenshots(
    paths=['tumor.bam', 'normal.bam'],
    regions=['chr1:1000000-2000000', 'chr2:3000000-4000000'],
    output_dir='./screenshots',
    genome='hg19'
)

# Save figures
for i, fig in enumerate(figures):
    fig.savefig(f'screenshot_{i}.png', dpi=300, bbox_inches='tight')
```

#### API Reference
```python
igver.load_screenshots(
    paths,              # List of input files
    regions,            # List of regions or BED file
    output_dir='/tmp',  # Output directory
    genome='hg19',      # Reference genome
    igv_dir='/opt/IGV_2.19.5',
    overwrite=True,     # Overwrite existing files
    remove_png=True,    # Remove temporary PNGs
    dpi=300,            # Figure resolution
    singularity_image='docker://sahuno/igver:latest',
    **kwargs            # Additional IGV options
)
```

## Supported File Formats

### Input Files
- **BAM** files (requires .bai index files)
- **BEDPE** files (for structural variants)
- **VCF** files (variant calls)
- **bigWig** files (coverage tracks)

### Region Files
- **BED3**: `chromosome<TAB>start<TAB>end`
- **BED6**: `chromosome<TAB>start<TAB>end<TAB>name<TAB>score<TAB>strand`
- **Text**: Custom format with optional annotations

### Output Formats
- **PNG** (default): Raster format, best for publications
- **SVG**: Vector format, scalable without quality loss
- **PDF**: Converted from SVG, requires `cairosvg` (`pip install igver[pdf]`)

## Output File Naming

- Single region: `chr1-1000000-2000000.png`
- BED with name: `chr1-1000000-2000000.gene_name.png`
- Multiple regions: `chr1-1000-2000.chr2-3000-4000.png`
- With annotation: `chr1-1000000-2000000.annotation.png`

## Examples

### Example 1: Simple Screenshot
```bash
igver -i sample.bam -r "chr1:1000000-2000000" -o ./
```
Creates: `./chr1-1000000-2000000.png`

### Example 2: Structural Variant Visualization
```bash
# Create a regions file for a translocation
echo -e "chr8:128750000-128760000\tchr14:106330000-106340000\ttranslocation" > sv_regions.bed

igver \
  -i tumor.bam normal.bam \
  -r sv_regions.bed \
  -o ./sv_screenshots
```

### Example 3: Different Output Formats
```bash
# Generate SVG (vector format)
igver -i sample.bam -r "chr1:1000000-2000000" -f svg -o ./

# Generate PDF (requires cairosvg)
pip install igver[pdf]  # Install PDF support
igver -i sample.bam -r "chr1:1000000-2000000" -f pdf -o ./
```

### Example 4: Custom IGV Preferences
```bash
# Create custom preferences
cat > custom_prefs.txt << EOF
colorBy TAG HP
sort READNAME
group TAG RG
EOF

igver \
  -i sample.bam \
  -r regions.bed \
  -c custom_prefs.txt \
  -o ./screenshots
```

## Advanced Usage

### Working with Haplotagged Reads
```bash
# Create IGV preferences for haplotype visualization
cat > haplotype_view.batch << EOF
group TAG HP
colorBy TAG HP
sort READNAME
EOF

igver \
  -i haplotagged.bam \
  -r regions.bed \
  -c haplotype_view.batch \
  -p 500 \
  -o ./haplotype_screenshots
```

### Batch Processing Multiple Samples
```python
import igver
import glob

# Process all BAM files in a directory
bam_files = glob.glob("samples/*.bam")
regions = ["chr1:1000000-2000000", "chr2:3000000-4000000"]

for bam in bam_files:
    sample_name = os.path.basename(bam).replace('.bam', '')
    figures = igver.load_screenshots(
        paths=[bam],
        regions=regions,
        output_dir=f'screenshots/{sample_name}'
    )
```

## Performance Tips

- **Pre-pull containers**: Download container images before running to avoid delays
- **Use absolute paths**: Provide absolute paths for files to avoid binding issues
- **Bind directories**: Use `-B` or `--bind` flags to mount data directories
- **Memory allocation**: Ensure sufficient memory for large genomic regions
- **Parallel processing**: Process multiple samples in parallel when possible

## Troubleshooting

### Container Issues
- **Permission denied**: Add `--bind` flags for your data directories
  ```bash
  singularity exec --bind /data,/home docker://sahuno/igver:latest igver.py ...
  ```
- **Image not found**: Pull the image first
  ```bash
  singularity pull docker://sahuno/igver:latest
  ```

### Common Errors
- **No screenshots generated**: 
  - Check if BAM files have indexes (.bai files)
  - Verify chromosome names match reference genome (chr1 vs 1)
  - Check output directory permissions

- **Region not found**:
  - Verify chromosome naming convention
  - Check if regions are within chromosome bounds
  - Ensure genome version matches your data

### IGV Display Issues
- **Screenshot width**: Modify IGV preferences file
  ```bash
  # In container: /opt/IGV_2.19.5/prefs.properties
  # Set: IGV.Bounds=0,0,800,480 for 800px width
  ```

## License

MIT License - see [LICENSE](LICENSE) file for details

## Authors

- Seongmin Choi ([@soymintc](https://github.com/soymintc)) - Original author
- Contributors welcome!

## Citation

If you use IGVer in your research, please cite:
```
Choi, S. (2024). IGVer: Automated IGV Screenshot Generation for Genomics. 
GitHub: https://github.com/shahcompbio/igver
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.