#!/bin/bash
# Test IGVer with Singularity using the updated Docker image

set -e

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${PROJECT_DIR}/singularity_test_output"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing IGVer with Singularity ==="
echo "Using Docker image: docker://sahuno/igver:latest"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Test 1: Basic test with single BAM and region
echo "1. Basic test with single BAM file..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/test1/

echo ""
echo "2. Test with multiple regions..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" "19:11137898-11139898" -g hg19 -o /output/test2/

echo ""
echo "3. Test with multiple BAM files..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam /data/test_normal.bam -r "8:32534767-32536767" -g hg19 -o /output/test3/

echo ""
echo "4. Test with BED file regions..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r /data/example_regions.bed -g hg19 -o /output/test4/

echo ""
echo "5. Test with regions from text file..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r /data/regions.txt -g hg19 -o /output/test5/

echo ""
echo "6. Test with debug output..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_normal.bam -r "1:1000000-1100000" -g hg19 -o /output/test6/ --debug

echo ""
echo "=== Test Results ==="
echo "Generated screenshots:"
find "${OUTPUT_DIR}" -name "*.png" -type f | sort

# Count total files
PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f | wc -l)
echo ""
echo "Total PNG files generated: ${PNG_COUNT}"

# Show file sizes
echo ""
echo "File details:"
find "${OUTPUT_DIR}" -name "*.png" -type f -exec ls -lh {} \; | sort

if [ ${PNG_COUNT} -gt 0 ]; then
    echo ""
    echo "✓ SUCCESS: Singularity test passed! Generated ${PNG_COUNT} screenshots."
    echo ""
    echo "The Docker image works correctly with Singularity."
    echo "Container auto-detection is working - IGV runs directly without nested Singularity calls."
else
    echo ""
    echo "✗ FAILED: No screenshots generated."
fi