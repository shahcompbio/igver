#!/bin/bash
# Test Singularity with explicit environment variable

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${PROJECT_DIR}/singularity_workaround_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing Singularity with Workaround ==="
echo ""

# Method 1: Set IGVER_IN_CONTAINER explicitly
echo "1. Testing with IGVER_IN_CONTAINER=1..."
singularity exec \
    --env IGVER_IN_CONTAINER=1 \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/method1/

# Method 2: Use --no-singularity flag
echo ""
echo "2. Testing with --no-singularity flag..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "19:11137898-11139898" -g hg19 -o /output/method2/ --no-singularity

echo ""
echo "Checking results:"
find "${OUTPUT_DIR}" -name "*.png" -type f

PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f | wc -l)
if [ ${PNG_COUNT} -gt 0 ]; then
    echo ""
    echo "SUCCESS: Generated ${PNG_COUNT} screenshots"
    echo ""
    echo "Workaround options:"
    echo "1. Use: singularity exec --env IGVER_IN_CONTAINER=1 ..."
    echo "2. Use: igver ... --no-singularity"
else
    echo ""
    echo "Still failing. Check diagnostic output."
fi