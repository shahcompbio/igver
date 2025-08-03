#!/usr/bin/env python3

import os
import sys
import tempfile
import pytest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from igver import igver


class TestOutputFormats:
    """Test different output format support"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_regions(self):
        """Sample regions for testing"""
        return ["chr1:1000000-2000000", "chr2:3000000-4000000"]
    
    def test_png_format_default(self, temp_dir, sample_regions):
        """Test PNG format (default)"""
        # Create batch script with default format
        batch_script, output_paths = igver.create_batch_script(
            paths=["dummy.bam"],
            regions=sample_regions,
            output_dir=temp_dir,
            genome='hg19'
        )
        
        # Check that PNG files are created
        assert len(output_paths) == 2
        assert all(path.endswith('.png') for path in output_paths)
        assert output_paths[0].endswith('chr1-1000000-2000000.png')
        assert output_paths[1].endswith('chr2-3000000-4000000.png')
    
    def test_svg_format(self, temp_dir, sample_regions):
        """Test SVG format output"""
        # Create batch script with SVG format
        batch_script, output_paths = igver.create_batch_script(
            paths=["dummy.bam"],
            regions=sample_regions,
            output_dir=temp_dir,
            genome='hg19',
            output_format='svg'
        )
        
        # Check that SVG files are created
        assert len(output_paths) == 2
        assert all(path.endswith('.svg') for path in output_paths)
        assert output_paths[0].endswith('chr1-1000000-2000000.svg')
        assert output_paths[1].endswith('chr2-3000000-4000000.svg')
    
    def test_pdf_format_creates_svg(self, temp_dir, sample_regions):
        """Test that PDF format creates SVG files first"""
        # Create batch script with PDF format
        batch_script, output_paths = igver.create_batch_script(
            paths=["dummy.bam"],
            regions=sample_regions,
            output_dir=temp_dir,
            genome='hg19',
            output_format='pdf'
        )
        
        # Check that SVG files are created (will be converted to PDF later)
        assert len(output_paths) == 2
        assert all(path.endswith('.svg') for path in output_paths)
    
    def test_batch_script_content(self, temp_dir):
        """Test that batch script contains correct snapshot commands"""
        regions = ["chr1:1000-2000"]
        
        # Test PNG
        batch_script, _ = igver.create_batch_script(
            paths=["test.bam"],
            regions=regions,
            output_dir=temp_dir,
            output_format='png'
        )
        
        with open(batch_script, 'r') as f:
            content = f.read()
        assert 'snapshot chr1-1000-2000.png' in content
        
        # Test SVG
        batch_script, _ = igver.create_batch_script(
            paths=["test.bam"],
            regions=regions,
            output_dir=temp_dir,
            output_format='svg'
        )
        
        with open(batch_script, 'r') as f:
            content = f.read()
        assert 'snapshot chr1-1000-2000.svg' in content
    
    def test_bed_file_with_formats(self, temp_dir):
        """Test BED file parsing with different formats"""
        # Create a simple BED file
        bed_content = "chr1\t1000\t2000\tregion1\n"
        bed_path = os.path.join(temp_dir, "test.bed")
        with open(bed_path, 'w') as f:
            f.write(bed_content)
        
        # Test PNG format
        png_paths, _ = igver._parse_bed_file(
            bed_path, temp_dir, output_format='png'
        )
        assert png_paths[0].endswith('chr1-1000-2000.region1.png')
        
        # Test SVG format
        svg_paths, _ = igver._parse_bed_file(
            bed_path, temp_dir, output_format='svg'
        )
        assert svg_paths[0].endswith('chr1-1000-2000.region1.svg')
        
        # Test PDF format (creates SVG)
        pdf_paths, _ = igver._parse_bed_file(
            bed_path, temp_dir, output_format='pdf'
        )
        assert pdf_paths[0].endswith('chr1-1000-2000.region1.svg')
    
    def test_region_string_with_formats(self, temp_dir):
        """Test region string parsing with different formats"""
        region = "chr1:1000-2000"
        
        # Test PNG
        paths, _ = igver._parse_region_string(
            region, temp_dir, output_format='png'
        )
        assert paths[0].endswith('.png')
        
        # Test SVG
        paths, _ = igver._parse_region_string(
            region, temp_dir, output_format='svg'
        )
        assert paths[0].endswith('.svg')
        
        # Test PDF (creates SVG)
        paths, _ = igver._parse_region_string(
            region, temp_dir, output_format='pdf'
        )
        assert paths[0].endswith('.svg')
    
    def test_pdf_conversion_error_without_cairosvg(self, temp_dir):
        """Test that PDF conversion fails gracefully without cairosvg"""
        # Mock the absence of cairosvg
        original_has_cairosvg = igver.HAS_CAIROSVG
        igver.HAS_CAIROSVG = False
        
        try:
            with pytest.raises(ImportError) as exc_info:
                igver._convert_svg_to_pdf(['dummy.svg'], False, 300, False)
            
            assert "cairosvg is required" in str(exc_info.value)
        finally:
            # Restore original value
            igver.HAS_CAIROSVG = original_has_cairosvg
    
    @pytest.mark.skipif(not igver.HAS_CAIROSVG, reason="cairosvg not installed")
    def test_svg_to_pdf_conversion(self, temp_dir):
        """Test SVG to PDF conversion"""
        # Create a dummy SVG file
        svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" fill="blue"/>
        </svg>'''
        
        svg_path = os.path.join(temp_dir, "test.svg")
        with open(svg_path, 'w') as f:
            f.write(svg_content)
        
        # Convert to PDF
        pdf_paths = igver._convert_svg_to_pdf([svg_path], False, 300, False)
        
        # Check PDF was created
        assert len(pdf_paths) == 1
        assert pdf_paths[0].endswith('.pdf')
        assert os.path.exists(pdf_paths[0])
        
        # Check SVG still exists (remove_svg=False)
        assert os.path.exists(svg_path)
        
        # Test with remove_svg=True
        svg_path2 = os.path.join(temp_dir, "test2.svg")
        with open(svg_path2, 'w') as f:
            f.write(svg_content)
        
        pdf_paths = igver._convert_svg_to_pdf([svg_path2], True, 300, False)
        
        # Check SVG was removed
        assert not os.path.exists(svg_path2)
        assert os.path.exists(pdf_paths[0])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])