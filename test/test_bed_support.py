#!/usr/bin/env python3

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from igver import igver


class TestBEDSupport:
    """Test BED file parsing functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_bed3_file(self, temp_dir):
        """Create a sample BED3 file"""
        bed_content = """chr1\t100000\t200000
chr2\t300000\t400000
chr3\t500000\t600000
"""
        bed_path = os.path.join(temp_dir, "test_regions.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        return bed_path
    
    @pytest.fixture
    def sample_bed6_file(self, temp_dir):
        """Create a sample BED6 file with names"""
        bed_content = """chr1\t100000\t200000\tregion1\t100\t+
chr2\t300000\t400000\tregion2\t200\t-
chr3\t500000\t600000\tregion3\t300\t+
# This is a comment
chr4\t700000\t800000\tregion4\t400\t.
"""
        bed_path = os.path.join(temp_dir, "test_regions_bed6.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        return bed_path
    
    @pytest.fixture
    def sample_bed_with_headers(self, temp_dir):
        """Create a BED file with track and browser lines"""
        bed_content = """track name="ItemRGBDemo" description="Item RGB demonstration" visibility=2 itemRgb="On"
browser position chr7:127471196-127495720
chr7\t127471196\t127472363\tPos1\t0\t+
chr7\t127472363\t127473530\tPos2\t0\t+
chr7\t127473530\t127474697\tPos3\t0\t+
"""
        bed_path = os.path.join(temp_dir, "test_with_headers.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        return bed_path
    
    def test_parse_bed3_file(self, sample_bed3_file, temp_dir):
        """Test parsing of BED3 format"""
        png_paths, region_content = igver._parse_bed_file(
            sample_bed3_file, 
            temp_dir
        )
        
        # Check that we got 3 regions
        assert len(png_paths) == 3
        
        # Check first region
        assert png_paths[0].endswith("chr1-100000-200000.png")
        
        # Check batch content
        assert "goto chr1:100000-200000" in region_content
        assert "goto chr2:300000-400000" in region_content
        assert "goto chr3:500000-600000" in region_content
    
    def test_parse_bed6_file(self, sample_bed6_file, temp_dir):
        """Test parsing of BED6 format with names"""
        png_paths, region_content = igver._parse_bed_file(
            sample_bed6_file,
            temp_dir
        )
        
        # Check that we got 4 regions (comment line should be skipped)
        assert len(png_paths) == 4
        
        # Check that names are included in filenames
        assert png_paths[0].endswith("chr1-100000-200000.region1.png")
        assert png_paths[1].endswith("chr2-300000-400000.region2.png")
        assert png_paths[2].endswith("chr3-500000-600000.region3.png")
        assert png_paths[3].endswith("chr4-700000-800000.region4.png")
    
    def test_parse_bed_with_headers(self, sample_bed_with_headers, temp_dir):
        """Test that track and browser lines are properly skipped"""
        png_paths, region_content = igver._parse_bed_file(
            sample_bed_with_headers,
            temp_dir
        )
        
        # Should have 3 regions (headers skipped)
        assert len(png_paths) == 3
        
        # Check regions
        assert png_paths[0].endswith("chr7-127471196-127472363.Pos1.png")
        assert png_paths[1].endswith("chr7-127472363-127473530.Pos2.png")
        assert png_paths[2].endswith("chr7-127473530-127474697.Pos3.png")
    
    def test_bed_file_with_custom_tag(self, sample_bed3_file, temp_dir):
        """Test BED file parsing with custom tag"""
        png_paths, region_content = igver._parse_bed_file(
            sample_bed3_file,
            temp_dir,
            tag="test_run"
        )
        
        # Check that tag is added to filenames
        assert png_paths[0].endswith("chr1-100000-200000.test_run.png")
        assert png_paths[1].endswith("chr2-300000-400000.test_run.png")
    
    def test_bed_file_with_preferences(self, sample_bed3_file, temp_dir):
        """Test BED file parsing with custom preferences"""
        png_paths, region_content = igver._parse_bed_file(
            sample_bed3_file,
            temp_dir,
            overlap_display="collapse",
            max_panel_height=300,
            additional_pref="colorBy TAG RG"
        )
        
        # Check that preferences are included
        assert "collapse" in region_content
        assert "maxPanelHeight 300" in region_content
        assert "colorBy TAG RG" in region_content
    
    def test_empty_bed_file(self, temp_dir):
        """Test handling of empty BED file"""
        bed_path = os.path.join(temp_dir, "empty.bed")
        with open(bed_path, 'w') as f:
            f.write("")
        
        png_paths, region_content = igver._parse_bed_file(bed_path, temp_dir)
        
        assert len(png_paths) == 0
        assert len(region_content) == 0
    
    def test_malformed_bed_file(self, temp_dir):
        """Test handling of malformed BED file"""
        bed_content = """chr1\t100000
chr2\t300000\t400000\textra
incomplete line
"""
        bed_path = os.path.join(temp_dir, "malformed.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        
        png_paths, region_content = igver._parse_bed_file(bed_path, temp_dir)
        
        # Should only parse the valid line
        assert len(png_paths) == 1
        assert png_paths[0].endswith("chr2-300000-400000.extra.png")


class TestGetPathsAndRegions:
    """Test the main region parsing function that handles both BED and text files"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_text_file(self, temp_dir):
        """Create a sample text format regions file"""
        text_content = """chr1:100000-200000
chr2:300000-400000 deletion
chr3:500000-600000 chr4:700000-800000 translocation
"""
        text_path = os.path.join(temp_dir, "test_regions.txt")
        with open(text_path, 'w') as f:
            f.write(text_content)
        return text_path
    
    def test_get_paths_detects_bed_file(self, temp_dir):
        """Test that .bed extension triggers BED parser"""
        bed_content = "chr1\t100000\t200000\n"
        bed_path = os.path.join(temp_dir, "regions.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        
        png_paths, _ = igver._get_paths_and_regions([bed_path], output_dir=temp_dir)
        
        assert len(png_paths) == 1
        assert "chr1-100000-200000.png" in png_paths[0]
    
    def test_get_paths_handles_text_file(self, sample_text_file, temp_dir):
        """Test that non-.bed files use text parser"""
        png_paths, _ = igver._get_paths_and_regions([sample_text_file], output_dir=temp_dir)
        
        # Text parser creates different output format
        assert len(png_paths) == 3
    
    def test_get_paths_handles_direct_regions(self, temp_dir):
        """Test direct region strings"""
        regions = ["chr1:100000-200000", "chr2:300000-400000"]
        png_paths, region_content = igver._get_paths_and_regions(
            regions, 
            output_dir=temp_dir
        )
        
        assert len(png_paths) == 2
        assert "goto chr1:100000-200000" in region_content
        assert "goto chr2:300000-400000" in region_content
    
    def test_mixed_input_types(self, temp_dir):
        """Test mixing direct regions and files"""
        # Create a BED file
        bed_content = "chr1\t100000\t200000\tbed_region\n"
        bed_path = os.path.join(temp_dir, "regions.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        
        # Mix file and direct region
        regions = [bed_path, "chr2:300000-400000"]
        png_paths, region_content = igver._get_paths_and_regions(
            regions,
            output_dir=temp_dir
        )
        
        assert len(png_paths) == 2
        assert any("bed_region" in path for path in png_paths)
        assert any("chr2-300000-400000" in path for path in png_paths)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])