# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

IGVer is a genomics visualization automation tool that generates IGV (Integrative Genomics Viewer) screenshots for multiple BAM files across multiple genomic regions. It's designed for bioinformatics workflows, particularly for visualizing genomic variants and structural variations.

## Key Commands

### Installation and Development
```bash
# Install in development mode
pip install -e .

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest test/test_cli.py

# Build distribution
python setup.py sdist bdist_wheel
```

### CLI Usage
```bash
# Basic usage
igver -i input.bam -r "chr1:1000-2000" -o output_dir

# Multiple BAM files and regions
igver -i sample1.bam sample2.bam -r regions.txt -o screenshots/

# With custom genome and container
igver -i input.bam -r "chr1:1000-2000" -g hg38 -sif /path/to/igver.sif
```

### Python API
```python
import igver

# Generate screenshots
figures = igver.load_screenshots(
    bam_paths=['sample1.bam', 'sample2.bam'],
    regions=['chr1:1000-2000', 'chr2:3000-4000'],
    outdir='screenshots/',
    genome='hg19'
)

# Create batch script only
igver.create_batch_script(bam_paths, regions, genome, outdir)
```

## Architecture

### Core Flow
1. **Input Processing** (`cli.py`): Parse BAM files and genomic regions
2. **Batch Script Generation** (`igver.py`): Create IGV batch commands
3. **Container Execution**: Run IGV in Singularity container with xvfb
4. **Output**: Screenshots saved as PNG files

### Key Components

**igver/igver.py**
- `load_screenshots()`: Main API entry point
- `create_batch_script()`: Generates IGV batch files
- `run_igv()`: Executes IGV via Singularity
- `load_image()`: Loads generated screenshots

**igver/cli.py**
- Command-line interface using argparse
- Handles file validation and argument parsing

### Container Architecture
- Uses Singularity containers for reproducibility
- Default image: `docker://quay.io/soymintc/igver`
- Runs IGV 2.19.5 in headless mode using xvfb

## Genomics-Specific Considerations

### Supported Genomes
- Human: hg19, hg38 (GRCh37, GRCh38)
- Mouse: mm10, mm39
- Custom genomes via `.genome` files

### File Format Support
- Primary: BAM files (requires .bai index)
- Additional: BEDPE, VCF, bigWig
- Regions: BED3/BED6 format (.bed files), text files (.txt), or chr:start-end notation
  - BED3: chromosome, start, end
  - BED6: chromosome, start, end, name, score, strand (name included in output)

### Structural Variation Visualization
The tool includes specialized settings for visualizing:
- Inversions
- Translocations
- Duplications
- Custom breakpoints

## Testing

Test files are in `test/` directory:
- `test_cli.py`: pytest-based CLI tests
- Sample BAM files with indices
- `regions.txt`: Example genomic regions
- IGV batch templates for different use cases

Run tests with: `pytest test/test_cli.py`

## Important Implementation Details

1. **Singularity Dependency**: The tool requires Singularity to be installed and accessible in PATH
2. **Display Handling**: Uses xvfb for headless operation - no X display required
3. **Output Naming**: Screenshots are named as `{bam_basename}_{region}.png`
4. **Genome Aliases**: Automatically maps genome aliases (e.g., GRCh38 → hg38)
5. **IGV Preferences**: Customizes IGV display settings for genomics visualization

## Development Task List

See `TASK_LIST.md` for the comprehensive development roadmap including:
- Phase 1: Standalone software optimization (IGV 2.19.5 update, BED file support)
- Phase 2: AI agent development (natural language interface, automated workflows)

## Future Agent Development Notes

For creating an agent to streamline genomics analysis:
1. The core `load_screenshots()` function can be wrapped for batch processing
2. Consider adding support for automated region detection from VCF files
3. The batch script generation is modular and can be extended for custom workflows
4. Container approach ensures reproducibility across different environments