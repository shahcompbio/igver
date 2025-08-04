# IGVer MCP Server

A Model Context Protocol (MCP) server that enables Claude Code to generate IGV screenshots programmatically using IGVer.

## Features

- Generate IGV screenshots from genomic regions or BED files
- Support for multiple input formats (BAM, VCF, bigWig, BEDPE)
- Batch processing capabilities
- Region validation
- Docker and Singularity container support
- Natural language interface through Claude Code

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/igver-mcp.git
cd igver-mcp

# Create virtual environment and install
uv venv
uv pip install -e .
```

### Using pip

```bash
# Clone and install
git clone https://github.com/yourusername/igver-mcp.git
cd igver-mcp
pip install -e .
```

## Claude Code Configuration

Add the following to your Claude Code settings file (`~/.config/claude/claude_desktop_settings.json`):

```json
{
  "mcpServers": {
    "igver": {
      "command": "uv",
      "args": ["run", "igver-mcp"],
      "env": {
        "IGVER_RUNTIME": "docker",
        "IGVER_DEFAULT_GENOME": "hg38"
      },
      "cwd": "/path/to/igver-mcp"
    }
  }
}
```

### Environment Variables

- `IGVER_RUNTIME`: Container runtime (`docker` or `singularity`)
- `IGVER_DEFAULT_GENOME`: Default reference genome (e.g., `hg19`, `hg38`)
- `IGVER_IMAGE`: Custom container image (default: `sahuno/igver:latest`)

## Usage Examples

Once configured, you can use natural language commands in Claude Code:

### Basic Screenshot
```
Take IGV screenshots of chr1:1000000-2000000 using sample.bam
```

### Using BED File
```
Generate IGV screenshots for all regions in @test/example_regions.bed with hg38 genome
```

### Multiple Files
```
Create IGV snapshots comparing tumor.bam and normal.bam at chr2:5000000-6000000
```

### Custom Options
```
Take high-resolution SVG screenshots of structural variants in sv_regions.bed using long_reads.bam
```

## Available Tools

### igver_screenshot
Generate IGV screenshots from genomic regions.

**Parameters:**
- `regions`: Genomic regions or BED file path
- `input_files`: List of input files (BAM/VCF/bigWig)
- `genome`: Reference genome (default: "hg19")
- `output_dir`: Output directory
- `format`: Output format (png/svg/pdf)
- `dpi`: Resolution for raster formats
- `options`: Additional IGV options

### igver_batch_screenshot
Process multiple screenshot requests from a configuration file.

**Parameters:**
- `batch_config`: Path to YAML/JSON configuration
- `output_base_dir`: Base output directory

### igver_validate_regions
Validate genomic regions or BED file.

**Parameters:**
- `regions`: Regions to validate
- `genome`: Reference genome

### igver_list_genomes
List available reference genomes and their aliases.

## Batch Configuration Example

Create a YAML file for batch processing:

```yaml
jobs:
  - name: sample1_variants
    regions: variants.bed
    input_files:
      - /data/sample1.bam
    genome: hg38
    format: png
    dpi: 300
    
  - name: sample2_coverage
    regions: "chr1:1000000-2000000 chr2:3000000-4000000"
    input_files:
      - /data/sample2.bigWig
    genome: hg38
    format: svg
```

## Container Support

### Docker (Recommended)
```bash
# Pull the latest IGVer image
docker pull sahuno/igver:latest

# The MCP server will automatically use Docker if available
```

### Singularity
```bash
# For HPC environments
singularity pull docker://sahuno/igver:latest

# Set runtime environment
export IGVER_RUNTIME=singularity
```

## Troubleshooting

### Common Issues

1. **Container not found**
   - Ensure Docker/Singularity is installed
   - Pull the IGVer image manually

2. **Permission denied**
   - Check file permissions
   - Ensure output directory is writable

3. **Region validation fails**
   - Verify chromosome naming (chr1 vs 1)
   - Check genome version matches your data

### Debug Mode

Enable debug logging by setting:
```bash
export IGVER_DEBUG=true
```

## Development

### Running Tests
```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=igver_mcp
```

### Code Quality
```bash
# Format code
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions:
- GitHub Issues: [igver-mcp/issues](https://github.com/yourusername/igver-mcp/issues)
- IGVer Documentation: [IGVer README](https://github.com/shahcompbio/igver)