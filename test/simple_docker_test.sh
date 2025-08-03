#!/bin/bash
# Simple test to verify Docker container can access files and run IGVer

set -e

echo "=== Simple IGVer Docker Test ==="
echo ""

# Get current directory
CURRENT_DIR=$(pwd)
echo "Current directory: $CURRENT_DIR"
echo ""

# Test 1: List test directory contents
echo "1. Checking test files in container:"
docker run --rm -v "$CURRENT_DIR:/workspace:ro" sahuno/igver:latest ls -la /workspace/test/*.bam
echo ""

# Test 2: Check IGVer can see the file
echo "2. Testing if IGVer can access the BAM file:"
docker run --rm -v "$CURRENT_DIR:/workspace:ro" sahuno/igver:latest python -c "
import os
bam_path = '/workspace/test/test_tumor.bam'
if os.path.exists(bam_path):
    print(f'✓ BAM file found: {bam_path}')
    print(f'  Size: {os.path.getsize(bam_path)} bytes')
else:
    print(f'✗ BAM file NOT found: {bam_path}')
"
echo ""

# Test 3: Run IGVer with minimal options
echo "3. Running IGVer with minimal options:"
mkdir -p simple_output
docker run --rm \
    -v "$CURRENT_DIR:/workspace:ro" \
    -v "$CURRENT_DIR/simple_output:/output" \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam -r "8:32534767-32536767" -o /output/

echo ""
echo "4. Checking output:"
ls -la simple_output/