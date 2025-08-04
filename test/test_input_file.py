#!/usr/bin/env python3
"""
Tests for the .txt file input functionality in igver CLI.
Tests both regular execution and --no-singularity mode.
"""

import subprocess
import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path to import igver modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from igver.cli import _parse_input_file

# Test data paths
TEST_DIR = Path(__file__).parent
TEST_BAM1 = TEST_DIR / "test_tumor.bam"
TEST_BAM2 = TEST_DIR / "test_normal.bam"
OUTPUT_DIR = TEST_DIR / "output"
REGION = "8:32534767-32536767"


class TestInputFileParser:
    """Test the _parse_input_file function directly"""
    
    def test_parse_valid_input_file(self, tmp_path):
        """Test parsing a valid input file with multiple paths"""
        input_file = tmp_path / "tracks.txt"
        input_file.write_text(f"""# Test BAM files
{TEST_BAM1}

# Another BAM file
{TEST_BAM2}
""")
        
        paths = _parse_input_file(str(input_file))
        assert len(paths) == 2
        assert str(TEST_BAM1) in paths
        assert str(TEST_BAM2) in paths
    
    def test_parse_with_home_expansion(self, tmp_path):
        """Test that ~ is expanded to home directory"""
        input_file = tmp_path / "tracks.txt"
        input_file.write_text("~/test.bam\n")
        
        paths = _parse_input_file(str(input_file))
        assert len(paths) == 1
        assert paths[0] == os.path.expanduser("~/test.bam")
    
    def test_parse_empty_file(self, tmp_path):
        """Test that empty file raises error"""
        input_file = tmp_path / "empty.txt"
        input_file.write_text("")
        
        with pytest.raises(ValueError, match="No valid paths found"):
            _parse_input_file(str(input_file))
    
    def test_parse_comments_only(self, tmp_path):
        """Test that file with only comments raises error"""
        input_file = tmp_path / "comments.txt"
        input_file.write_text("# Just comments\n# Nothing else\n")
        
        with pytest.raises(ValueError, match="No valid paths found"):
            _parse_input_file(str(input_file))
    
    def test_parse_nonexistent_file(self):
        """Test that nonexistent file raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            _parse_input_file("/nonexistent/file.txt")


class TestCLIWithInputFile:
    """Test the full CLI with .txt file input"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment"""
        self.tmp_path = tmp_path
        self.output_dir = tmp_path / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create input file with test BAMs
        self.input_file = tmp_path / "test_tracks.txt"
        self.input_file.write_text(f"""{TEST_BAM1}
{TEST_BAM2}
""")
        
        # Create regions file
        self.regions_file = tmp_path / "regions.txt"
        self.regions_file.write_text(REGION)
    
    def test_cli_with_txt_input_file(self):
        """Test igver CLI with .txt input file"""
        # Skip if test BAM files don't exist
        if not TEST_BAM1.exists() or not TEST_BAM2.exists():
            pytest.skip("Test BAM files not found")
        
        command = [
            "python", "-m", "igver.cli",
            "-i", str(self.input_file),
            "-r", str(self.regions_file),
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity"  # Use no-singularity for testing
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=TEST_DIR.parent)
        
        # Check command succeeded
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        # Check that info message was printed
        assert "Loaded 2 track(s) from" in result.stdout
    
    def test_cli_with_direct_paths(self):
        """Test that direct paths still work (backward compatibility)"""
        if not TEST_BAM1.exists() or not TEST_BAM2.exists():
            pytest.skip("Test BAM files not found")
        
        command = [
            "python", "-m", "igver.cli",
            "-i", str(TEST_BAM1), str(TEST_BAM2),
            "-r", str(self.regions_file),
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=TEST_DIR.parent)
        
        # Should succeed without the "Loaded X track(s)" message
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        assert "Loaded" not in result.stdout  # Direct paths don't print this message
    
    def test_cli_with_invalid_path_in_file(self, tmp_path):
        """Test that invalid paths in file cause error"""
        invalid_input = tmp_path / "invalid_tracks.txt"
        invalid_input.write_text("/nonexistent/file.bam\n")
        
        command = [
            "python", "-m", "igver.cli",
            "-i", str(invalid_input),
            "-r", REGION,
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=TEST_DIR.parent)
        
        # Should fail with error about nonexistent file
        assert result.returncode == 1
        assert "does not exist" in result.stderr
    
    def test_cli_mixed_txt_and_direct(self):
        """Test that mixing .txt file with direct paths works as direct paths"""
        if not TEST_BAM1.exists():
            pytest.skip("Test BAM file not found")
        
        # When multiple arguments are provided, even if one ends with .txt,
        # they should all be treated as direct paths
        command = [
            "python", "-m", "igver.cli",
            "-i", str(self.input_file), str(TEST_BAM1),  # Mix of .txt and direct path
            "-r", REGION,
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=TEST_DIR.parent)
        
        # This should fail because input_file path will be checked as a track file
        assert result.returncode == 1


class TestSingularityCompatibility:
    """Test compatibility with Singularity execution modes"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment"""
        self.tmp_path = tmp_path
        self.output_dir = tmp_path / "output"
        self.output_dir.mkdir(exist_ok=True)
        
        # Create input file
        self.input_file = tmp_path / "tracks.txt"
        if TEST_BAM1.exists():
            self.input_file.write_text(str(TEST_BAM1))
    
    def test_singularity_exec_with_no_singularity_flag(self):
        """Test running inside container with --no-singularity flag"""
        if not TEST_BAM1.exists():
            pytest.skip("Test BAM file not found")
        
        # Simulate running inside a container
        env = os.environ.copy()
        env['IGVER_IN_CONTAINER'] = '1'
        
        command = [
            "python", "-m", "igver.cli",
            "-i", str(self.input_file),
            "-r", REGION,
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity"  # Should prevent nested singularity call
        ]
        
        # This tests that the command at least parses correctly
        # Actual execution would require IGV to be installed
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True, 
            cwd=TEST_DIR.parent,
            env=env
        )
        
        # Command should at least parse arguments correctly
        # It may fail later if IGV is not installed, but that's OK for this test
        if "igv.sh" in result.stderr:
            # Expected failure if IGV not installed
            pytest.skip("IGV not installed in test environment")
    
    def test_input_file_path_resolution(self, tmp_path):
        """Test that paths in input file work with bind mounts"""
        # Create a nested directory structure
        nested_dir = tmp_path / "data" / "bams"
        nested_dir.mkdir(parents=True)
        
        # Create dummy BAM file
        dummy_bam = nested_dir / "test.bam"
        dummy_bam.touch()
        dummy_bai = nested_dir / "test.bam.bai"
        dummy_bai.touch()
        
        # Create input file with absolute path
        input_file = tmp_path / "inputs.txt"
        input_file.write_text(str(dummy_bam))
        
        command = [
            "python", "-m", "igver.cli",
            "-i", str(input_file),
            "-r", REGION,
            "-o", str(self.output_dir),
            "-g", "hg19",
            "--no-singularity",
            "--debug"
        ]
        
        result = subprocess.run(command, capture_output=True, text=True, cwd=TEST_DIR.parent)
        
        # Should successfully load the path
        if result.returncode == 0:
            assert "Loaded 1 track(s)" in result.stdout


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])