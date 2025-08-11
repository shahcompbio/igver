"""End-to-end tests for IGVer MCP server."""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from igver_mcp.server import IGVerMCPServer
from igver_mcp.handlers import IGVerHandlers
from igver_mcp.utils import validate_regions, parse_bed_file


class TestE2E:
    """End-to-end test suite for IGVer MCP."""
    
    @pytest.fixture
    async def server(self):
        """Create test server instance."""
        return IGVerMCPServer()
    
    @pytest.fixture
    async def temp_dir(self):
        """Create temporary directory for test outputs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    async def sample_bed_file(self, temp_dir):
        """Create a sample BED file for testing."""
        bed_content = """# Test BED file
chr1\t1000000\t2000000\tregion1
chr2\t5000000\t6000000\tregion2
chr3\t10000000\t11000000\tregion3
"""
        bed_path = Path(temp_dir) / "test_regions.bed"
        bed_path.write_text(bed_content)
        return str(bed_path)
    
    @pytest.fixture
    async def sample_bam_file(self, temp_dir):
        """Create a mock BAM file for testing."""
        bam_path = Path(temp_dir) / "test_sample.bam"
        bam_path.touch()
        # Also create index file
        bai_path = Path(temp_dir) / "test_sample.bam.bai"
        bai_path.touch()
        return str(bam_path)
    
    @pytest.fixture
    async def batch_config(self, temp_dir, sample_bam_file):
        """Create a batch configuration file."""
        config = {
            "jobs": [
                {
                    "name": "test_job1",
                    "regions": "chr1:1000000-2000000",
                    "input_files": [sample_bam_file],
                    "genome": "hg38",
                    "format": "png"
                },
                {
                    "name": "test_job2",
                    "regions": "chr2:5000000-6000000",
                    "input_files": [sample_bam_file],
                    "genome": "hg19",
                    "format": "svg"
                }
            ]
        }
        config_path = Path(temp_dir) / "batch_config.json"
        config_path.write_text(json.dumps(config))
        return str(config_path)
    
    @pytest.mark.asyncio
    async def test_region_validation(self):
        """Test region validation functionality."""
        # Valid regions
        valid_regions = [
            ("chr1:1000000-2000000", "hg19"),
            ("chrX:50000000-51000000", "hg38"),
            ("1:1000-2000", "hg19"),
            ("chr2:1,000,000-2,000,000", "hg38"),  # with commas
        ]
        
        for region, genome in valid_regions:
            is_valid, message = await validate_regions(region, genome)
            assert is_valid, f"Region {region} should be valid: {message}"
        
        # Invalid regions
        invalid_regions = [
            ("chr1:2000000-1000000", "hg19"),  # end < start
            ("chr1:-1000-2000", "hg19"),  # negative start
            ("invalid_format", "hg19"),  # bad format
            ("chr1:1000000-999999999999", "hg19"),  # exceeds chromosome size
        ]
        
        for region, genome in invalid_regions:
            is_valid, message = await validate_regions(region, genome)
            assert not is_valid, f"Region {region} should be invalid"
    
    @pytest.mark.asyncio
    async def test_bed_file_parsing(self, sample_bed_file):
        """Test BED file parsing."""
        regions = await parse_bed_file(sample_bed_file)
        
        assert len(regions) == 3
        assert regions[0]['region'] == "chr1:1000000-2000000"
        assert regions[0]['name'] == "region1"
        assert regions[1]['region'] == "chr2:5000000-6000000"
        assert regions[2]['chrom'] == "chr3"
    
    @pytest.mark.asyncio
    @patch('igver_mcp.handlers.asyncio.create_subprocess_exec')
    async def test_screenshot_generation(
        self,
        mock_subprocess,
        server,
        temp_dir,
        sample_bam_file
    ):
        """Test basic screenshot generation."""
        # Mock subprocess execution
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Success", b"")
        mock_subprocess.return_value = mock_process
        
        # Create mock output file
        output_file = Path(temp_dir) / "chr1-1000000-2000000.png"
        output_file.touch()
        
        handlers = IGVerHandlers()
        result = await handlers.generate_screenshot(
            regions="chr1:1000000-2000000",
            input_files=[sample_bam_file],
            genome="hg38",
            output_dir=temp_dir,
            format="png",
            dpi=300
        )
        
        assert result['status'] == 'success'
        assert result['output_dir'] == temp_dir
        assert len(result['files']) == 1
        assert result['files'][0]['name'] == "chr1-1000000-2000000.png"
        mock_subprocess.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('igver_mcp.handlers.asyncio.create_subprocess_exec')
    async def test_batch_processing(
        self,
        mock_subprocess,
        temp_dir,
        batch_config,
        sample_bam_file
    ):
        """Test batch screenshot processing."""
        # Mock subprocess execution
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Success", b"")
        mock_subprocess.return_value = mock_process
        
        # Create mock output files
        job1_dir = Path(temp_dir) / "test_job1"
        job1_dir.mkdir()
        (job1_dir / "chr1-1000000-2000000.png").touch()
        
        job2_dir = Path(temp_dir) / "test_job2"
        job2_dir.mkdir()
        (job2_dir / "chr2-5000000-6000000.svg").touch()
        
        handlers = IGVerHandlers()
        result = await handlers.batch_screenshot(
            batch_config=batch_config,
            output_base_dir=temp_dir
        )
        
        assert result['total_jobs'] == 2
        assert result['successful'] == 2
        assert result['failed'] == 0
        assert len(result['results']) == 2
    
    @pytest.mark.asyncio
    async def test_genome_listing(self):
        """Test genome listing functionality."""
        handlers = IGVerHandlers()
        genomes = await handlers.list_available_genomes()
        
        assert 'supported_genomes' in genomes
        assert 'hg19' in genomes['supported_genomes']
        assert 'hg38' in genomes['supported_genomes']
        assert 'aliases' in genomes
        assert 'GRCh38' in genomes['aliases']['hg38']
    
    @pytest.mark.asyncio
    @patch('igver_mcp.utils.shutil.which')
    def test_container_runtime_detection(self, mock_which):
        """Test container runtime detection."""
        from igver_mcp.utils import detect_container_runtime
        
        # Test Docker detection
        mock_which.return_value = '/usr/bin/docker'
        assert detect_container_runtime() == 'docker'
        
        # Test Singularity detection
        mock_which.side_effect = lambda x: '/usr/bin/singularity' if x == 'singularity' else None
        assert detect_container_runtime() == 'singularity'
        
        # Test no runtime available
        mock_which.return_value = None
        assert detect_container_runtime() is None
    
    @pytest.mark.asyncio
    @patch('igver_mcp.handlers.asyncio.create_subprocess_exec')
    async def test_docker_command_building(
        self,
        mock_subprocess,
        temp_dir,
        sample_bam_file
    ):
        """Test Docker command construction."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Success", b"")
        mock_subprocess.return_value = mock_process
        
        handlers = IGVerHandlers()
        handlers.runtime = "docker"
        
        # Build command
        cmd = await handlers._build_igver_command(
            regions="chr1:1000000-2000000",
            input_files=[sample_bam_file],
            genome="hg38",
            output_dir=temp_dir,
            format="png",
            dpi=300
        )
        
        assert cmd[0] == "docker"
        assert "run" in cmd
        assert "--rm" in cmd
        assert "sahuno/igver:latest" in cmd
        assert "-v" in cmd  # Volume mounts
    
    @pytest.mark.asyncio
    @patch('igver_mcp.handlers.asyncio.create_subprocess_exec')
    async def test_singularity_command_building(
        self,
        mock_subprocess,
        temp_dir,
        sample_bam_file
    ):
        """Test Singularity command construction."""
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Success", b"")
        mock_subprocess.return_value = mock_process
        
        handlers = IGVerHandlers()
        handlers.runtime = "singularity"
        
        # Build command
        cmd = await handlers._build_igver_command(
            regions="chr1:1000000-2000000",
            input_files=[sample_bam_file],
            genome="hg38",
            output_dir=temp_dir,
            format="png",
            dpi=300
        )
        
        assert cmd[0] == "singularity"
        assert "exec" in cmd
        assert "-B" in cmd  # Bind mounts
        assert "--no-singularity" in cmd  # Important flag
        assert "docker://sahuno/igver:latest" in cmd
    
    @pytest.mark.asyncio
    async def test_error_handling(self, temp_dir):
        """Test error handling for invalid inputs."""
        handlers = IGVerHandlers()
        
        # Test with non-existent file
        with pytest.raises(ValueError, match="Input file not found"):
            await handlers.generate_screenshot(
                regions="chr1:1000000-2000000",
                input_files=["/non/existent/file.bam"],
                output_dir=temp_dir
            )
        
        # Test with invalid batch config
        with pytest.raises(ValueError, match="Batch config file not found"):
            await handlers.batch_screenshot(
                batch_config="/non/existent/config.yaml",
                output_base_dir=temp_dir
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])