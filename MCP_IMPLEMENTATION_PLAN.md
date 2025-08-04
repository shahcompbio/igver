# IGVer MCP (Model Context Protocol) Implementation Plan

## Overview
This document outlines the plan to create an MCP server for IGVer that enables Claude Code to generate IGV screenshots programmatically. The MCP will allow users to execute commands like:
```
"Take IGV screenshots of the @test/example_regions.bed with hg38 genome"
```

## Project Structure

### Directory Layout
```
igver-mcp/
├── pyproject.toml          # uv project configuration
├── README.md               # MCP-specific documentation
├── src/
│   └── igver_mcp/
│       ├── __init__.py
│       ├── server.py       # Main MCP server implementation
│       ├── handlers.py     # Request handlers
│       └── utils.py        # Utility functions
├── tests/
│   ├── test_server.py
│   └── test_handlers.py
└── examples/
    ├── example_regions.bed
    └── sample_usage.md
```

## Implementation Details

### 1. MCP Server Architecture

The MCP server will expose the following tools:

#### `igver_screenshot`
Generate IGV screenshots from genomic regions.

**Parameters:**
- `regions`: String or file path (BED file or space-separated regions)
- `input_files`: List of BAM/VCF/bigWig file paths
- `genome`: Reference genome (default: "hg19")
- `output_dir`: Output directory for screenshots
- `format`: Output format (png/svg/pdf, default: "png")
- `dpi`: Resolution (default: 300)
- `options`: Additional IGV options (optional)

#### `igver_batch_screenshot`
Process multiple region sets with different configurations.

**Parameters:**
- `batch_config`: Path to YAML/JSON configuration file
- `output_base_dir`: Base output directory

#### `igver_validate_regions`
Validate BED file or region strings before processing.

**Parameters:**
- `regions`: String or file path to validate
- `genome`: Reference genome for validation

### 2. Technology Stack

- **Python Package Manager**: uv (for speed and robustness)
- **MCP Framework**: Official MCP Python SDK
- **Container Runtime**: Docker/Singularity support
- **Dependencies**:
  - `mcp-python` (MCP SDK)
  - `igver` (core functionality)
  - `pydantic` (data validation)
  - `aiofiles` (async file operations)

### 3. Container Strategy

## Advantages and Disadvantages of Singularity Approach

### Advantages of Singularity

1. **HPC Compatibility**
   - Widely adopted in academic/research computing environments
   - No root privileges required for execution
   - Better integration with cluster job schedulers

2. **Security**
   - Read-only container by default
   - No daemon process required
   - Better suited for multi-user environments

3. **Reproducibility**
   - Immutable containers ensure consistent results
   - SIF format is portable and self-contained
   - Version pinning is straightforward

4. **Resource Efficiency**
   - Lower overhead compared to Docker
   - Native performance for I/O operations
   - Efficient handling of large genomic files

### Disadvantages of Singularity

1. **Installation Complexity**
   - Requires Singularity/Apptainer installation on host
   - Not available by default on most systems
   - Version compatibility issues between Singularity/Apptainer

2. **Development Workflow**
   - Less convenient for local development
   - Limited tooling compared to Docker ecosystem
   - Harder to debug container issues

3. **Cross-Platform Support**
   - Limited Windows/macOS support
   - Primarily Linux-focused
   - May require VM on non-Linux systems

4. **MCP Integration Challenges**
   - Additional layer of complexity in MCP server
   - Need to handle container detection (--no-singularity flag)
   - Path mapping between host and container

### Recommended Approach

For the MCP implementation, we should:

1. **Support Both Docker and Singularity**
   - Auto-detect available runtime
   - Provide configuration options
   - Fall back gracefully

2. **Default to Docker for MCP**
   - Better integration with development workflows
   - Easier for most users to install
   - More predictable behavior

3. **Provide Singularity Option**
   - For HPC environments
   - For security-conscious deployments
   - Document configuration clearly

## MCP Server Implementation

### Core Server Code Structure

```python
# src/igver_mcp/server.py
import os
from typing import List, Dict, Any, Optional
from mcp.server import Server
from mcp.types import Tool, TextContent
import asyncio
from pathlib import Path

class IGVerMCPServer:
    def __init__(self):
        self.server = Server("igver-mcp")
        self.setup_handlers()
    
    def setup_handlers(self):
        @self.server.tool()
        async def igver_screenshot(
            regions: str,
            input_files: List[str],
            genome: str = "hg19",
            output_dir: str = "./igv_screenshots",
            format: str = "png",
            dpi: int = 300,
            options: Optional[Dict[str, Any]] = None
        ) -> str:
            # Implementation here
            pass
```

### Configuration File

```yaml
# igver-mcp-config.yaml
server:
  name: "igver-mcp"
  version: "1.0.0"
  
runtime:
  preferred: "docker"  # or "singularity"
  docker:
    image: "sahuno/igver:latest"
    auto_pull: true
  singularity:
    image: "docker://sahuno/igver:latest"
    bind_paths:
      - "/home"
      - "/data"
  
defaults:
  genome: "hg19"
  dpi: 300
  format: "png"
  output_dir: "./igv_screenshots"
```

## Integration with Claude Code

### 1. Installation Steps

```bash
# Clone the repository
git clone https://github.com/yourusername/igver-mcp.git
cd igver-mcp

# Install with uv
uv venv
uv pip install -e .

# Or install from PyPI (once published)
uv pip install igver-mcp
```

### 2. Claude Code Configuration

Add to your Claude Code settings (`claude_desktop_settings.json`):

```json
{
  "mcpServers": {
    "igver": {
      "command": "uv",
      "args": ["run", "igver-mcp"],
      "env": {
        "IGVER_RUNTIME": "docker",
        "IGVER_DEFAULT_GENOME": "hg38"
      }
    }
  }
}
```

### 3. Usage Examples

Once configured, users can interact with IGVer through natural language:

```
# Basic usage
"Take IGV screenshots of chr1:1000000-2000000 using sample.bam"

# Using BED file
"Generate IGV screenshots for all regions in @test/example_regions.bed with hg38 genome"

# Multiple files
"Create IGV snapshots comparing tumor.bam and normal.bam at chr2:5000000-6000000"

# Custom options
"Take high-resolution SVG screenshots of structural variants in sv_regions.bed using long_reads.bam"
```

## Development Timeline

### Phase 1: Core MCP Server (Week 1)
- [ ] Set up uv project structure
- [ ] Implement basic MCP server
- [ ] Create igver_screenshot handler
- [ ] Add error handling and validation

### Phase 2: Container Integration (Week 2)
- [ ] Implement Docker support
- [ ] Add Singularity support with auto-detection
- [ ] Handle path mapping and permissions
- [ ] Test with both container runtimes

### Phase 3: Advanced Features (Week 3)
- [ ] Implement batch processing
- [ ] Add region validation tool
- [ ] Create configuration management
- [ ] Add caching for performance

### Phase 4: Testing & Documentation (Week 4)
- [ ] Write comprehensive tests
- [ ] Create user documentation
- [ ] Add example notebooks
- [ ] Prepare for distribution

## Distribution Strategy

### 1. PyPI Package
- Publish as `igver-mcp` on PyPI
- Include all dependencies except IGVer itself
- Provide clear installation instructions

### 2. GitHub Release
- Maintain on GitHub with releases
- Include pre-built configurations
- Provide Docker Compose setup

### 3. MCP Registry
- Submit to official MCP registry
- Include metadata and examples
- Maintain compatibility with MCP updates

## Security Considerations

1. **File Access Control**
   - Validate all file paths
   - Restrict access to allowed directories
   - Sanitize user inputs

2. **Container Security**
   - Use official IGVer images only
   - Limit container capabilities
   - Implement resource limits

3. **Data Privacy**
   - Don't log genomic data
   - Clear temporary files
   - Respect user data boundaries

## Performance Optimization

1. **Caching Strategy**
   - Cache container images locally
   - Reuse container instances
   - Cache common region validations

2. **Parallel Processing**
   - Support concurrent screenshot generation
   - Implement job queuing
   - Optimize for batch operations

3. **Resource Management**
   - Set memory limits
   - Implement timeouts
   - Clean up resources properly

## Testing Strategy

### Unit Tests
- Test each handler function
- Validate input parsing
- Test error conditions

### Integration Tests
- Test with real IGVer containers
- Validate file generation
- Test different genomic formats

### End-to-End Tests
- Test Claude Code integration
- Validate natural language parsing
- Test real-world scenarios

## Maintenance Plan

1. **Version Compatibility**
   - Track IGVer updates
   - Maintain backward compatibility
   - Document breaking changes

2. **User Support**
   - Create troubleshooting guide
   - Maintain FAQ section
   - Provide example scripts

3. **Community Engagement**
   - Accept contributions
   - Respond to issues
   - Regular updates

## Conclusion

This MCP implementation will make IGVer accessible to a broader audience through Claude Code's natural language interface. By supporting both Docker and Singularity, we ensure compatibility across different computing environments while maintaining ease of use for the majority of users.