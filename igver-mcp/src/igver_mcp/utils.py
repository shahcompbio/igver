"""Utility functions for IGVer MCP server."""

import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import aiofiles


async def validate_file_path(path: str) -> bool:
    """Check if file exists and is readable."""
    try:
        path_obj = Path(path)
        return path_obj.exists() and path_obj.is_file()
    except Exception:
        return False


async def ensure_directory(path: str) -> None:
    """Ensure directory exists, create if necessary."""
    Path(path).mkdir(parents=True, exist_ok=True)


def detect_container_runtime() -> Optional[str]:
    """Detect if running in Docker or Singularity container."""
    
    # Check for Docker
    if os.path.exists('/.dockerenv'):
        return "docker"
    
    # Check for Singularity
    if os.environ.get('SINGULARITY_CONTAINER'):
        return "singularity"
    
    # Check if docker is available
    if shutil.which('docker'):
        return "docker"
    
    # Check if singularity is available
    if shutil.which('singularity'):
        return "singularity"
    
    return None


async def validate_regions(region: str, genome: str) -> Tuple[bool, str]:
    """
    Validate genomic region format.
    
    Expected formats:
    - chr1:1000-2000
    - chr1:1,000-2,000 (with commas)
    - 1:1000-2000 (without chr prefix)
    """
    
    # Remove commas from numbers
    region = region.replace(',', '')
    
    # Pattern for genomic coordinates
    pattern = r'^(chr)?([0-9XYM]+):(\d+)-(\d+)$'
    match = re.match(pattern, region)
    
    if not match:
        return False, f"Invalid region format: {region}"
    
    _, chrom, start, end = match.groups()
    start_pos = int(start)
    end_pos = int(end)
    
    # Validate positions
    if start_pos <= 0:
        return False, "Start position must be greater than 0"
    
    if end_pos <= start_pos:
        return False, "End position must be greater than start position"
    
    # Check against known chromosome sizes (simplified)
    chrom_sizes = get_chromosome_sizes(genome)
    if chrom in chrom_sizes:
        max_size = chrom_sizes[chrom]
        if end_pos > max_size:
            return False, f"End position exceeds chromosome {chrom} size ({max_size})"
    
    return True, "Valid region"


async def parse_bed_file(bed_path: str) -> List[Dict[str, str]]:
    """Parse BED file and extract regions."""
    regions = []
    
    async with aiofiles.open(bed_path, 'r') as f:
        async for line in f:
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('\t')
            
            if len(parts) < 3:
                continue
            
            chrom = parts[0]
            start = parts[1]
            end = parts[2]
            
            region_dict = {
                'region': f"{chrom}:{start}-{end}",
                'chrom': chrom,
                'start': start,
                'end': end
            }
            
            # BED6 format includes name
            if len(parts) >= 4:
                region_dict['name'] = parts[3]
            
            regions.append(region_dict)
    
    return regions


def get_chromosome_sizes(genome: str) -> Dict[str, int]:
    """Get chromosome sizes for validation (simplified subset)."""
    
    # Simplified chromosome sizes for common genomes
    sizes = {
        'hg19': {
            '1': 249250621, '2': 242951149, '3': 198022430,
            '4': 191154276, '5': 180915260, '6': 171115067,
            '7': 159138663, '8': 146364022, '9': 141213431,
            '10': 135534747, '11': 135006516, '12': 133851895,
            '13': 115169878, '14': 107349540, '15': 102531392,
            '16': 90354753, '17': 81195210, '18': 78077248,
            '19': 59128983, '20': 63025520, '21': 48129895,
            '22': 51304566, 'X': 155270560, 'Y': 59373566,
            'M': 16569
        },
        'hg38': {
            '1': 248956422, '2': 242193529, '3': 198295559,
            '4': 190214555, '5': 181538259, '6': 170805979,
            '7': 159345973, '8': 145138636, '9': 138394717,
            '10': 133797422, '11': 135086622, '12': 133275309,
            '13': 114364328, '14': 107043718, '15': 101991189,
            '16': 90338345, '17': 83257441, '18': 80373285,
            '19': 58617616, '20': 64444167, '21': 46709983,
            '22': 50818468, 'X': 156040895, 'Y': 57227415,
            'M': 16569
        }
    }
    
    return sizes.get(genome, {})


def get_genome_aliases() -> Dict[str, List[str]]:
    """Get genome name aliases."""
    
    return {
        'hg19': ['hg19', 'GRCh37', 'b37'],
        'hg38': ['hg38', 'GRCh38', 'b38'],
        'mm10': ['mm10', 'GRCm38'],
        'mm39': ['mm39', 'GRCm39']
    }


async def create_temp_config(
    config_content: str,
    suffix: str = '.batch'
) -> str:
    """Create temporary configuration file."""
    
    import tempfile
    
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix=suffix,
        delete=False
    ) as f:
        f.write(config_content)
        return f.name