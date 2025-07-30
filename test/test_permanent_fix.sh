#!/bin/bash
# Test the permanent fix for IGVer in Docker

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/permanent_fix_test"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing Permanent Fix for IGVer in Docker ==="
echo ""

# Test 1: Run with auto-detection (should work in Docker)
echo "1. Testing auto-detection in Docker container..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/auto/ --debug

echo ""
echo "2. Testing with IGVER_IN_CONTAINER environment variable..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam -r "19:11137898-11139898" -g hg19 -o /output/env/ --debug

echo ""
echo "3. Testing with --no-singularity flag..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam -r "1:1000000-1100000" -g hg19 -o /output/flag/ --no-singularity --debug

echo ""
echo "4. Testing multiple regions..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam /workspace/test/test_normal.bam \
          -r "8:32534767-32536767" "19:11137898-11139898" \
          -g hg19 -o /output/multi/

echo ""
echo "5. Checking all outputs..."
echo "Generated files:"
find "${OUTPUT_DIR}" -name "*.png" -type f | sort

# Count files
PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f | wc -l)
echo ""
echo "Total PNG files generated: ${PNG_COUNT}"

if [ ${PNG_COUNT} -gt 0 ]; then
    echo ""
    echo "SUCCESS: Permanent fix is working! Generated ${PNG_COUNT} screenshots."
else
    echo ""
    echo "FAILED: No screenshots generated."
fi