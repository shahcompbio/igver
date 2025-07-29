#!/usr/bin/env python3

import os
import sys
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from igver import igver
from igver import cli


class TestIGVVersion:
    """Test that IGV version has been updated to 2.19.5"""
    
    def test_default_igv_dir_in_load_screenshots(self):
        """Test default IGV directory in load_screenshots function"""
        # Check the function signature default value
        import inspect
        sig = inspect.signature(igver.load_screenshots)
        igv_dir_default = sig.parameters['igv_dir'].default
        
        assert igv_dir_default == "/opt/IGV_2.19.5"
    
    def test_default_igv_dir_in_run_igv(self):
        """Test default IGV directory in run_igv function"""
        import inspect
        sig = inspect.signature(igver.run_igv)
        igv_dir_default = sig.parameters['igv_dir'].default
        
        assert igv_dir_default == "/opt/IGV_2.19.5"
    
    def test_cli_default_igv_dir(self):
        """Test default IGV directory in CLI arguments"""
        # Read CLI source to check default value
        cli_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "igver",
            "cli.py"
        )
        
        with open(cli_path, 'r') as f:
            cli_content = f.read()
        
        # Check for the default IGV directory in the argparse definition
        assert 'default="/opt/IGV_2.19.5"' in cli_content
    
    def test_dockerfile_igv_version(self):
        """Test that Dockerfile contains IGV 2.19.5"""
        dockerfile_path = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "docker", 
            "Dockerfile"
        )
        
        if os.path.exists(dockerfile_path):
            with open(dockerfile_path, 'r') as f:
                dockerfile_content = f.read()
            
            # Check for IGV 2.19.5 references
            assert "IGV_2.19.5.zip" in dockerfile_content
            assert "/opt/IGV_2.19.5" in dockerfile_content
            assert "2.17.4" not in dockerfile_content  # Old version should be gone
    
    def test_no_old_version_references(self):
        """Ensure no references to old IGV version remain in Python code"""
        # Check igver.py
        igver_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "igver",
            "igver.py"
        )
        
        with open(igver_path, 'r') as f:
            igver_content = f.read()
        
        assert "2.17.4" not in igver_content
        assert "IGV_2.17.4" not in igver_content
        
        # Check cli.py
        cli_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "igver",
            "cli.py"
        )
        
        with open(cli_path, 'r') as f:
            cli_content = f.read()
        
        assert "2.17.4" not in cli_content
        assert "IGV_2.17.4" not in cli_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])