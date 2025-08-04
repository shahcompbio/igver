"""Request handlers for IGVer MCP server."""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import aiofiles
import yaml

from .utils import (
    validate_file_path,
    validate_regions,
    parse_bed_file,
    detect_container_runtime,
    ensure_directory,
    get_genome_aliases
)

logger = logging.getLogger(__name__)


class IGVerHandlers:
    """Handler class for IGVer MCP operations."""
    
    def __init__(self):
        self.runtime = detect_container_runtime()
        self.default_image = "sahuno/igver:latest"
        
    async def generate_screenshot(
        self,
        regions: str,
        input_files: List[str],
        genome: str = "hg19",
        output_dir: str = "./igv_screenshots",
        format: str = "png",
        dpi: int = 300,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate IGV screenshots using IGVer."""
        
        # Validate inputs
        for file_path in input_files:
            if not await validate_file_path(file_path):
                raise ValueError(f"Input file not found: {file_path}")
        
        # Create output directory
        await ensure_directory(output_dir)
        
        # Prepare IGVer command
        cmd = await self._build_igver_command(
            regions=regions,
            input_files=input_files,
            genome=genome,
            output_dir=output_dir,
            format=format,
            dpi=dpi,
            options=options
        )
        
        # Execute command
        logger.info(f"Executing command: {' '.join(cmd)}")
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"IGVer failed: {error_msg}")
            
            # Parse output files
            output_files = await self._find_output_files(output_dir, format)
            
            return {
                "status": "success",
                "output_dir": output_dir,
                "files": output_files,
                "command": " ".join(cmd),
                "runtime": self.runtime or "native"
            }
            
        except Exception as e:
            logger.error(f"Screenshot generation failed: {e}")
            raise
    
    async def batch_screenshot(
        self,
        batch_config: str,
        output_base_dir: str = "./igv_batch_output"
    ) -> Dict[str, Any]:
        """Process batch screenshot requests."""
        
        # Validate config file
        if not await validate_file_path(batch_config):
            raise ValueError(f"Batch config file not found: {batch_config}")
        
        # Load configuration
        async with aiofiles.open(batch_config, 'r') as f:
            content = await f.read()
            
        if batch_config.endswith('.yaml') or batch_config.endswith('.yml'):
            config = yaml.safe_load(content)
        else:
            config = json.loads(content)
        
        # Process each job
        results = []
        for i, job in enumerate(config.get('jobs', [])):
            job_name = job.get('name', f'job_{i}')
            output_dir = os.path.join(output_base_dir, job_name)
            
            try:
                result = await self.generate_screenshot(
                    regions=job['regions'],
                    input_files=job['input_files'],
                    genome=job.get('genome', 'hg19'),
                    output_dir=output_dir,
                    format=job.get('format', 'png'),
                    dpi=job.get('dpi', 300),
                    options=job.get('options')
                )
                results.append({
                    "job": job_name,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                results.append({
                    "job": job_name,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "total_jobs": len(config.get('jobs', [])),
            "successful": sum(1 for r in results if r['status'] == 'success'),
            "failed": sum(1 for r in results if r['status'] == 'failed'),
            "results": results
        }
    
    async def validate_regions(
        self,
        regions: str,
        genome: str = "hg19"
    ) -> Dict[str, Any]:
        """Validate genomic regions or BED file."""
        
        # Check if regions is a file path
        if os.path.exists(regions):
            # It's a BED file
            parsed_regions = await parse_bed_file(regions)
            validation_results = []
            
            for region in parsed_regions:
                is_valid, message = await validate_regions(region['region'], genome)
                validation_results.append({
                    "region": region['region'],
                    "name": region.get('name'),
                    "valid": is_valid,
                    "message": message
                })
            
            return {
                "type": "bed_file",
                "file": regions,
                "total_regions": len(parsed_regions),
                "valid_regions": sum(1 for r in validation_results if r['valid']),
                "invalid_regions": sum(1 for r in validation_results if not r['valid']),
                "details": validation_results
            }
        else:
            # It's a region string
            is_valid, message = await validate_regions(regions, genome)
            return {
                "type": "region_string",
                "region": regions,
                "valid": is_valid,
                "message": message,
                "genome": genome
            }
    
    async def list_available_genomes(self) -> Dict[str, List[str]]:
        """List available reference genomes."""
        
        genomes = get_genome_aliases()
        
        return {
            "supported_genomes": list(genomes.keys()),
            "aliases": genomes,
            "default": "hg19",
            "note": "Use either the primary name or any of its aliases"
        }
    
    async def _build_igver_command(
        self,
        regions: str,
        input_files: List[str],
        genome: str,
        output_dir: str,
        format: str,
        dpi: int,
        options: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """Build the IGVer command based on runtime environment."""
        
        # Base command components
        igver_args = [
            "-i", *input_files,
            "-r", regions,
            "-o", output_dir,
            "-g", genome,
            "-f", format,
            "--dpi", str(dpi)
        ]
        
        # Add optional arguments
        if options:
            if options.get('max_panel_height'):
                igver_args.extend(["-p", str(options['max_panel_height'])])
            if options.get('overlap_display'):
                igver_args.extend(["-d", options['overlap_display']])
            if options.get('igv_config'):
                igver_args.extend(["-c", options['igv_config']])
        
        # Build command based on runtime
        if self.runtime == "docker":
            # Docker command
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{os.path.abspath(output_dir)}:/output",
            ]
            
            # Mount input file directories
            mounted_dirs = set()
            for file_path in input_files:
                dir_path = os.path.dirname(os.path.abspath(file_path))
                if dir_path not in mounted_dirs:
                    cmd.extend(["-v", f"{dir_path}:{dir_path}"])
                    mounted_dirs.add(dir_path)
            
            # Mount regions file if it's a file path
            if os.path.exists(regions):
                regions_dir = os.path.dirname(os.path.abspath(regions))
                if regions_dir not in mounted_dirs:
                    cmd.extend(["-v", f"{regions_dir}:{regions_dir}"])
            
            cmd.extend([
                self.default_image,
                "igver",
                *igver_args
            ])
            
        elif self.runtime == "singularity":
            # Singularity command
            cmd = [
                "singularity", "exec",
            ]
            
            # Bind mount directories
            bind_paths = [output_dir]
            for file_path in input_files:
                bind_paths.append(os.path.dirname(os.path.abspath(file_path)))
            
            if os.path.exists(regions):
                bind_paths.append(os.path.dirname(os.path.abspath(regions)))
            
            # Unique bind paths
            unique_binds = list(set(bind_paths))
            for bind_path in unique_binds:
                cmd.extend(["-B", f"{bind_path}:{bind_path}"])
            
            cmd.extend([
                f"docker://{self.default_image}",
                "igver",
                *igver_args,
                "--no-singularity"  # Important flag for Singularity
            ])
            
        else:
            # Native installation
            cmd = ["igver", *igver_args]
        
        return cmd
    
    async def _find_output_files(self, output_dir: str, format: str) -> List[Dict[str, str]]:
        """Find generated output files."""
        
        output_path = Path(output_dir)
        pattern = f"*.{format}"
        
        files = []
        for file_path in output_path.glob(pattern):
            file_info = {
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "format": format
            }
            files.append(file_info)
        
        return sorted(files, key=lambda x: x['name'])