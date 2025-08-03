#!/usr/bin/env python3
"""
Integration test for output format functionality.
This script tests the complete workflow with different output formats.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_cli_formats():
    """Test CLI with different output formats"""
    test_results = []
    
    # Use test BAM files if they exist
    test_bam = "test/test_tumor.bam"
    if not os.path.exists(test_bam):
        print(f"Warning: {test_bam} not found. Using dummy path for batch script generation only.")
        test_bam = "dummy.bam"
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test 1: PNG format (default)
        print("\n1. Testing PNG format (default)...")
        cmd = [
            sys.executable, "-m", "igver.cli",
            "-i", test_bam,
            "-r", "chr1:1000000-2000000",
            "-o", tmpdir
        ]
        
        try:
            # This will fail without Singularity, but we can check if batch script is created
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Exit code: {result.returncode}")
            
            # Check for batch file creation
            batch_files = list(Path(tmpdir).glob("*.batch"))
            if batch_files:
                with open(batch_files[0], 'r') as f:
                    content = f.read()
                    if "snapshot chr1-1000000-2000000.png" in content:
                        print("   ✓ PNG batch script created correctly")
                        test_results.append(("PNG default", True))
                    else:
                        print("   ✗ PNG snapshot command not found")
                        test_results.append(("PNG default", False))
        except Exception as e:
            print(f"   Error: {e}")
            test_results.append(("PNG default", False))
        
        # Clean up
        for f in Path(tmpdir).glob("*"):
            f.unlink()
        
        # Test 2: SVG format
        print("\n2. Testing SVG format...")
        cmd = [
            sys.executable, "-m", "igver.cli",
            "-i", test_bam,
            "-r", "chr1:1000000-2000000",
            "-o", tmpdir,
            "-f", "svg"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Exit code: {result.returncode}")
            
            batch_files = list(Path(tmpdir).glob("*.batch"))
            if batch_files:
                with open(batch_files[0], 'r') as f:
                    content = f.read()
                    if "snapshot chr1-1000000-2000000.svg" in content:
                        print("   ✓ SVG batch script created correctly")
                        test_results.append(("SVG format", True))
                    else:
                        print("   ✗ SVG snapshot command not found")
                        test_results.append(("SVG format", False))
        except Exception as e:
            print(f"   Error: {e}")
            test_results.append(("SVG format", False))
        
        # Clean up
        for f in Path(tmpdir).glob("*"):
            f.unlink()
        
        # Test 3: PDF format
        print("\n3. Testing PDF format...")
        cmd = [
            sys.executable, "-m", "igver.cli",
            "-i", test_bam,
            "-r", "chr1:1000000-2000000",
            "-o", tmpdir,
            "-f", "pdf"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(f"   Command: {' '.join(cmd)}")
            print(f"   Exit code: {result.returncode}")
            
            batch_files = list(Path(tmpdir).glob("*.batch"))
            if batch_files:
                with open(batch_files[0], 'r') as f:
                    content = f.read()
                    # PDF format should create SVG first
                    if "snapshot chr1-1000000-2000000.svg" in content:
                        print("   ✓ PDF batch script created correctly (SVG intermediate)")
                        test_results.append(("PDF format", True))
                    else:
                        print("   ✗ PDF snapshot command not found")
                        test_results.append(("PDF format", False))
        except Exception as e:
            print(f"   Error: {e}")
            test_results.append(("PDF format", False))
    
    # Summary
    print("\n" + "="*50)
    print("Test Summary:")
    print("="*50)
    for test_name, passed in test_results:
        status = "PASS" if passed else "FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(test_results)
    passed = sum(1 for _, p in test_results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return all(p for _, p in test_results)


def test_python_api_formats():
    """Test Python API with different formats"""
    print("\n" + "="*50)
    print("Testing Python API Format Support")
    print("="*50)
    
    import igver
    
    test_results = []
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test batch script creation for each format
        formats = ['png', 'svg', 'pdf']
        
        for fmt in formats:
            print(f"\nTesting {fmt.upper()} format via API...")
            try:
                batch_script, output_paths = igver.create_batch_script(
                    paths=['dummy.bam'],
                    regions=['chr1:1000-2000', 'chr2:3000-4000'],
                    output_dir=tmpdir,
                    output_format=fmt
                )
                
                # Check output paths
                expected_ext = 'svg' if fmt == 'pdf' else fmt
                if all(path.endswith(f'.{expected_ext}') for path in output_paths):
                    print(f"   ✓ {fmt.upper()} output paths correct")
                    test_results.append((f"API {fmt}", True))
                else:
                    print(f"   ✗ {fmt.upper()} output paths incorrect: {output_paths}")
                    test_results.append((f"API {fmt}", False))
                
                # Clean up
                if os.path.exists(batch_script):
                    os.unlink(batch_script)
                    
            except Exception as e:
                print(f"   ✗ Error: {e}")
                test_results.append((f"API {fmt}", False))
    
    # Test PDF conversion function
    print("\nTesting PDF conversion function...")
    if igver.HAS_CAIROSVG:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test SVG
            svg_path = os.path.join(tmpdir, "test.svg")
            with open(svg_path, 'w') as f:
                f.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
                       '<rect width="100" height="100" fill="blue"/></svg>')
            
            try:
                pdf_paths = igver._convert_svg_to_pdf([svg_path], False, 300, False)
                if os.path.exists(pdf_paths[0]) and pdf_paths[0].endswith('.pdf'):
                    print("   ✓ PDF conversion successful")
                    test_results.append(("PDF conversion", True))
                else:
                    print("   ✗ PDF conversion failed")
                    test_results.append(("PDF conversion", False))
            except Exception as e:
                print(f"   ✗ Error: {e}")
                test_results.append(("PDF conversion", False))
    else:
        print("   ⚠ cairosvg not installed, skipping PDF conversion test")
    
    # Summary
    print("\n" + "-"*50)
    total = len(test_results)
    passed = sum(1 for _, p in test_results if p)
    print(f"API Tests: {passed}/{total} passed")
    
    return all(p for _, p in test_results)


if __name__ == "__main__":
    print("IGVer Output Format Integration Tests")
    print("=====================================")
    
    # Run tests
    cli_passed = test_cli_formats()
    api_passed = test_python_api_formats()
    
    # Overall summary
    print("\n" + "="*50)
    print("OVERALL SUMMARY")
    print("="*50)
    print(f"CLI Tests: {'PASSED' if cli_passed else 'FAILED'}")
    print(f"API Tests: {'PASSED' if api_passed else 'FAILED'}")
    print(f"\nAll Tests: {'PASSED' if cli_passed and api_passed else 'FAILED'}")
    
    sys.exit(0 if cli_passed and api_passed else 1)