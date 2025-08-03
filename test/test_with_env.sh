#!/bin/bash
# Test with explicit IGVER_IN_CONTAINER=1

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/env_test_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing with IGVER_IN_CONTAINER=1 ==="
echo ""

# This should definitely work
echo "Running with local code and IGVER_IN_CONTAINER=1..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e PYTHONPATH=/opt/igver \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python -m igver.cli -i /workspace/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --debug

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/" 2>/dev/null || echo "No output directory"
find "${OUTPUT_DIR}" -name "*.png" 2>/dev/null || echo "No PNG files"

PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null | wc -l)
if [ ${PNG_COUNT} -gt 0 ]; then
    echo ""
    echo "SUCCESS! Generated ${PNG_COUNT} screenshot(s)."
    echo "The fix is working when IGVER_IN_CONTAINER=1 is set."
    echo ""
    echo "Once you rebuild the Docker image with the updated Dockerfile,"
    echo "this environment variable will be set automatically."
else
    echo ""
    echo "Still failing. Let's check what happened..."
fi