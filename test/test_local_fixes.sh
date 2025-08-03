#!/bin/bash
# Test the local fixes by mounting the updated code into the Docker container

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/local_fix_test"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing Local Fixes in Docker Container ==="
echo "Mounting local code from: ${PROJECT_DIR}"
echo ""

# Test 1: Override the container's igver code with local fixed version
echo "1. Testing with local code mounted (should auto-detect container)..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e PYTHONPATH=/opt/igver \
    sahuno/igver:latest \
    python -m igver.cli -i /workspace/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/auto/ --debug

echo ""
echo "2. Testing with IGVER_IN_CONTAINER=1..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e PYTHONPATH=/opt/igver \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python -m igver.cli -i /workspace/test/test_tumor.bam -r "19:11137898-11139898" -g hg19 -o /output/env/

echo ""
echo "3. Testing with --no-singularity flag..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e PYTHONPATH=/opt/igver \
    sahuno/igver:latest \
    python -m igver.cli -i /workspace/test/test_tumor.bam -r "1:1000000-1100000" -g hg19 -o /output/flag/ --no-singularity

echo ""
echo "4. Verifying container detection is working..."
docker run --rm \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -e PYTHONPATH=/opt/igver \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/opt/igver')
from igver.igver import is_running_in_container
print('Container detected:', is_running_in_container())
print('Should use Singularity:', not is_running_in_container())
"

echo ""
echo "5. Checking outputs..."
echo "Generated files:"
find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null | sort

PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null | wc -l)
echo ""
if [ ${PNG_COUNT} -gt 0 ]; then
    echo "SUCCESS: Local fixes are working! Generated ${PNG_COUNT} screenshots."
    echo ""
    echo "Next steps:"
    echo "1. Commit and push your changes to GitHub"
    echo "2. Rebuild the Docker image with: ./build_and_push_docker_with_log.sh"
else
    echo "FAILED: No screenshots generated. Check the debug output above."
fi