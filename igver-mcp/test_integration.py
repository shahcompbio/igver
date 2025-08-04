#!/usr/bin/env python3
"""Integration test for IGVer MCP - simulates Claude Code usage."""

import asyncio
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from igver_mcp.handlers import IGVerHandlers
from igver_mcp.utils import detect_container_runtime


async def test_mcp_integration():
    """Test the MCP integration as Claude Code would use it."""
    
    print("🧪 IGVer MCP Integration Test")
    print("=" * 50)
    
    # Initialize handlers
    handlers = IGVerHandlers()
    runtime = detect_container_runtime()
    print(f"✓ Detected runtime: {runtime or 'native'}")
    
    # Test 1: List available genomes
    print("\n1. Testing genome listing...")
    try:
        genomes = await handlers.list_available_genomes()
        print(f"✓ Available genomes: {', '.join(genomes['supported_genomes'])}")
    except Exception as e:
        print(f"✗ Failed to list genomes: {e}")
        return False
    
    # Test 2: Validate regions
    print("\n2. Testing region validation...")
    test_regions = [
        "chr1:1000000-2000000",
        "chrX:50000000-51000000",
        "invalid_region"
    ]
    
    for region in test_regions:
        try:
            result = await handlers.validate_regions(region, "hg38")
            status = "✓" if result.get('valid', False) else "✗"
            print(f"{status} {region}: {result.get('message', 'Unknown')}")
        except Exception as e:
            print(f"✗ Error validating {region}: {e}")
    
    # Test 3: Validate BED file
    print("\n3. Testing BED file validation...")
    bed_file = Path(__file__).parent / "examples" / "example_regions.bed"
    if bed_file.exists():
        try:
            result = await handlers.validate_regions(str(bed_file), "hg38")
            print(f"✓ BED file validation: {result['valid_regions']}/{result['total_regions']} regions valid")
        except Exception as e:
            print(f"✗ Failed to validate BED file: {e}")
    else:
        print("⚠ BED file not found, skipping test")
    
    # Test 4: Simulate screenshot command (without actual execution)
    print("\n4. Testing command building...")
    try:
        # This would be called by Claude Code
        cmd = await handlers._build_igver_command(
            regions="chr1:1000000-2000000",
            input_files=["/path/to/sample.bam"],
            genome="hg38",
            output_dir="./test_output",
            format="png",
            dpi=300
        )
        print(f"✓ Command built successfully:")
        print(f"  {' '.join(cmd[:5])}...")
    except Exception as e:
        print(f"✗ Failed to build command: {e}")
    
    print("\n" + "=" * 50)
    print("✓ Integration test completed!")
    print("\nTo use in Claude Code:")
    print("1. Copy the claude_desktop_settings.json to your Claude settings")
    print("2. Update the 'cwd' path to point to this directory")
    print("3. Restart Claude Code")
    print("4. Try: 'List available genomes for IGVer'")
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_mcp_integration())
    sys.exit(0 if success else 1)