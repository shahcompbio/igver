# Setting up IGVer MCP with Claude Code

This guide walks you through setting up the IGVer MCP server to work with Claude Code.

## Prerequisites

1. **Python 3.8+** installed
2. **uv** package manager installed:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```
3. **Docker** or **Singularity** installed
4. **Claude Code** desktop app installed

## Installation Steps

### 1. Clone and Install IGVer MCP

```bash
# Clone the repository
git clone <repository-url> igver-mcp
cd igver-mcp

# Create virtual environment and install
uv venv
uv pip install -e .

# Verify installation
uv run igver-mcp --help
```

### 2. Configure Claude Code

Locate your Claude Code settings file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_settings.json`
- **Linux**: `~/.config/claude/claude_desktop_settings.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_settings.json`

Add the IGVer MCP configuration:

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
      "cwd": "/absolute/path/to/igver-mcp"
    }
  }
}
```

**Important**: Replace `/absolute/path/to/igver-mcp` with the actual path to your igver-mcp directory.

### 3. Pull the IGVer Container

```bash
# For Docker
docker pull sahuno/igver:latest

# For Singularity
singularity pull docker://sahuno/igver:latest
```

### 4. Test the Setup

1. Restart Claude Code
2. Check if the MCP server is loaded by asking:
   ```
   List available reference genomes for IGVer
   ```

## Configuration Options

### Environment Variables

You can customize the behavior by modifying the environment variables in the configuration:

```json
"env": {
  "IGVER_RUNTIME": "docker",        // or "singularity"
  "IGVER_DEFAULT_GENOME": "hg38",   // or "hg19", "mm10", etc.
  "IGVER_IMAGE": "sahuno/igver:latest",  // custom image
  "IGVER_DEBUG": "true"             // enable debug logging
}
```

### Using Singularity Instead of Docker

If you're in an HPC environment or prefer Singularity:

```json
"env": {
  "IGVER_RUNTIME": "singularity",
  "IGVER_DEFAULT_GENOME": "hg38"
}
```

## Testing the Integration

### Basic Test

Try these commands in Claude Code:

1. **Simple screenshot**:
   ```
   Take an IGV screenshot of chr1:1000000-2000000 using test.bam
   ```

2. **Using BED file**:
   ```
   Generate screenshots for regions in regions.bed using sample.bam
   ```

3. **List genomes**:
   ```
   What reference genomes are available in IGVer?
   ```

### Test with Example Files

The MCP includes example files in the `examples/` directory:

```
cd igver-mcp/examples
```

Try:
```
Take IGV screenshots of example_regions.bed using my_sample.bam with hg38 genome
```

## Troubleshooting

### MCP Server Not Loading

1. Check Claude Code logs:
   - Help → Show Logs
   - Look for errors related to "igver"

2. Verify the path in settings is correct:
   ```bash
   ls /path/to/igver-mcp/src/igver_mcp/server.py
   ```

3. Test the server manually:
   ```bash
   cd /path/to/igver-mcp
   uv run igver-mcp
   ```

### Container Issues

1. **Docker not found**:
   ```bash
   # Check Docker installation
   docker --version
   
   # Start Docker daemon if needed
   sudo systemctl start docker  # Linux
   ```

2. **Singularity not found**:
   ```bash
   # Check Singularity installation
   singularity --version
   ```

3. **Image pull fails**:
   ```bash
   # Manual pull
   docker pull sahuno/igver:latest
   ```

### Permission Issues

1. **Output directory**:
   - Ensure write permissions for output directories
   - Use absolute paths when possible

2. **Input files**:
   - Check file permissions
   - Ensure BAM index files (.bai) exist

### Debug Mode

Enable debug logging to troubleshoot issues:

1. Update Claude Code settings:
   ```json
   "env": {
     "IGVER_DEBUG": "true"
   }
   ```

2. Check logs for detailed error messages

## Advanced Usage

### Custom IGV Preferences

Create a custom IGV preferences file:

```bash
cat > ~/igv_prefs.batch << EOF
colorBy TAG HP
sort READNAME
EOF
```

Then use in Claude Code:
```
Take a screenshot with custom IGV settings from ~/igv_prefs.batch
```

### Batch Processing

Create a batch configuration file:

```yaml
# batch_jobs.yaml
jobs:
  - name: sample1
    regions: regions.bed
    input_files: [sample1.bam]
    genome: hg38
  - name: sample2
    regions: "chr1:1000000-2000000"
    input_files: [sample2.bam]
    genome: hg38
```

Then process:
```
Run batch IGV screenshots using batch_jobs.yaml
```

## Support

For issues:
1. Check the [README](README.md)
2. Review [example usage](examples/sample_usage.md)
3. Open an issue on GitHub