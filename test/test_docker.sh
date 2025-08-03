#!/bin/bash
# Test script for IGVer Docker container

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_DIR="${SCRIPT_DIR}/test"
OUTPUT_DIR="${SCRIPT_DIR}/test_docker_output"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}Testing IGVer Docker container...${NC}"
echo -e "Using test BAM files from: ${TEST_DIR}"
echo -e "Output will be saved to: ${OUTPUT_DIR}"
echo ""

# Test 1: Basic single region
echo -e "${YELLOW}Test 1: Basic single region screenshot${NC}"
docker run --rm \
    -v "${TEST_DIR}:/input:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /input/test_tumor.bam -r "8:32534767-32536767" -o /output/test1/

# Test 2: Multiple regions from text file
echo -e "${YELLOW}Test 2: Multiple regions from text file${NC}"
docker run --rm \
    -v "${TEST_DIR}:/input:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /input/test_tumor.bam /input/test_normal.bam -r /input/regions.txt -o /output/test2/

# Test 3: BED file input
echo -e "${YELLOW}Test 3: BED file regions${NC}"
docker run --rm \
    -v "${TEST_DIR}:/input:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /input/test_tumor.bam -r /input/example_regions.bed -o /output/test3/

# Test 4: Custom genome (hg19)
echo -e "${YELLOW}Test 4: Custom genome specification${NC}"
docker run --rm \
    -v "${TEST_DIR}:/input:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /input/test_tumor.bam -r "19:11137898-11139898" -g hg19 -o /output/test4/

# Test 5: Test help
echo -e "${YELLOW}Test 5: Help command${NC}"
docker run --rm sahuno/igver:latest igver --help

# Check results
echo ""
echo -e "${GREEN}Test completed! Checking output files...${NC}"
echo "Generated screenshots:"
find "${OUTPUT_DIR}" -name "*.png" -type f | sort

# Count files
PNG_COUNT=$(find "${OUTPUT_DIR}" -name "*.png" -type f | wc -l)
echo ""
echo -e "${GREEN}Total PNG files generated: ${PNG_COUNT}${NC}"

# Display file sizes
echo ""
echo "File details:"
ls -lh "${OUTPUT_DIR}"/*/bam_snapshots/*.png 2>/dev/null || ls -lh "${OUTPUT_DIR}"/*/*.png 2>/dev/null

echo ""
echo -e "${GREEN}Docker test completed successfully!${NC}"
echo "You can view the generated screenshots in: ${OUTPUT_DIR}"