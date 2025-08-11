#!/usr/bin/env python3
"""Main MCP server implementation for IGVer."""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent

from .handlers import IGVerHandlers
from .utils import validate_file_path, detect_container_runtime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IGVerMCPServer:
    """MCP Server for IGVer functionality."""
    
    def __init__(self):
        self.server = Server("igver-mcp")
        self.handlers = IGVerHandlers()
        self.setup_tools()
        
    def setup_tools(self):
        """Register all available tools with the MCP server."""
        
        @self.server.tool()
        async def igver_screenshot(
            regions: str,
            input_files: List[str],
            genome: str = "hg19",
            output_dir: str = "./igv_screenshots",
            format: str = "png",
            dpi: int = 300,
            options: Optional[Dict[str, Any]] = None
        ) -> List[TextContent]:
            """
            Generate IGV screenshots from genomic regions.
            
            Args:
                regions: Genomic regions (e.g., "chr1:1000-2000") or path to BED file
                input_files: List of BAM/VCF/bigWig file paths
                genome: Reference genome (default: hg19)
                output_dir: Output directory for screenshots
                format: Output format (png/svg/pdf)
                dpi: Resolution for raster formats
                options: Additional IGV options
                
            Returns:
                List of generated file paths
            """
            try:
                result = await self.handlers.generate_screenshot(
                    regions=regions,
                    input_files=input_files,
                    genome=genome,
                    output_dir=output_dir,
                    format=format,
                    dpi=dpi,
                    options=options
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error generating screenshot: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.tool()
        async def igver_batch_screenshot(
            batch_config: str,
            output_base_dir: str = "./igv_batch_output"
        ) -> List[TextContent]:
            """
            Process multiple screenshot requests from a configuration file.
            
            Args:
                batch_config: Path to YAML/JSON configuration file
                output_base_dir: Base directory for all outputs
                
            Returns:
                Summary of generated screenshots
            """
            try:
                result = await self.handlers.batch_screenshot(
                    batch_config=batch_config,
                    output_base_dir=output_base_dir
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.tool()
        async def igver_validate_regions(
            regions: str,
            genome: str = "hg19"
        ) -> List[TextContent]:
            """
            Validate genomic regions or BED file.
            
            Args:
                regions: Regions string or path to BED file
                genome: Reference genome for validation
                
            Returns:
                Validation results
            """
            try:
                result = await self.handlers.validate_regions(
                    regions=regions,
                    genome=genome
                )
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                logger.error(f"Error validating regions: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
        
        @self.server.tool()
        async def igver_list_genomes() -> List[TextContent]:
            """
            List available reference genomes.
            
            Returns:
                List of supported genome assemblies
            """
            try:
                genomes = await self.handlers.list_available_genomes()
                return [TextContent(type="text", text=json.dumps(genomes, indent=2))]
            except Exception as e:
                logger.error(f"Error listing genomes: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def run(self):
        """Run the MCP server."""
        async with self.server:
            await self.server.run()


def main():
    """Main entry point for the MCP server."""
    # Set up environment
    os.environ["IGVER_MCP_VERSION"] = "1.0.0"
    
    # Detect container runtime
    runtime = detect_container_runtime()
    if runtime:
        logger.info(f"Detected container runtime: {runtime}")
        os.environ["IGVER_RUNTIME"] = runtime
    
    # Create and run server
    server = IGVerMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()