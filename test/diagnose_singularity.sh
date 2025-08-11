#!/bin/bash
# Diagnose why Singularity execution is failing

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== Diagnosing Singularity Execution ==="
echo ""

# Test 1: Check container detection inside Singularity
echo "1. Testing container detection in Singularity..."
singularity exec docker://sahuno/igver:latest python -c "
import os
print('Environment variables:')
print('  IGVER_IN_CONTAINER:', os.environ.get('IGVER_IN_CONTAINER', 'not set'))
print('  SINGULARITY_CONTAINER:', os.environ.get('SINGULARITY_CONTAINER', 'not set'))
print('  SINGULARITY_NAME:', os.environ.get('SINGULARITY_NAME', 'not set'))
print('')

# Check if our detection function exists and works
try:
    from igver.igver import is_running_in_container
    print('is_running_in_container():', is_running_in_container())
except Exception as e:
    print('Error importing:', e)
"

echo ""
echo "2. Testing if igver command is available..."
singularity exec docker://sahuno/igver:latest which igver || echo "igver not found"
singularity exec docker://sahuno/igver:latest igver --help | head -5

echo ""
echo "3. Testing with debug output..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${PROJECT_DIR}/singularity_test_output:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --debug 2>&1 | head -50

echo ""
echo "4. Check what happens when we run IGV directly..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    docker://sahuno/igver:latest \
    bash -c "cd /opt/IGV_2.19.5 && ./igv.sh --version 2>&1 || echo 'IGV version check failed'"

echo ""
echo "5. Test with explicit environment variable..."
singularity exec \
    --env IGVER_IN_CONTAINER=1 \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${PROJECT_DIR}/singularity_test_output:/output" \
    docker://sahuno/igver:latest \
    python -c "
import os
print('IGVER_IN_CONTAINER:', os.environ.get('IGVER_IN_CONTAINER'))
from igver.igver import is_running_in_container
print('is_running_in_container():', is_running_in_container())
"