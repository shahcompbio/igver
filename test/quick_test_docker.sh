#!/bin/bash
# Quick test of IGVer Docker container with a single BAM file

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_BAM="${SCRIPT_DIR}/test/test_tumor.bam"
OUTPUT_DIR="${SCRIPT_DIR}/docker_test_output"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}Quick Docker test of IGVer...${NC}"
echo "Input BAM: ${TEST_BAM}"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Run the test
echo -e "${YELLOW}Running IGVer with Docker...${NC}"
docker run --rm \
    -v "${SCRIPT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /app/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/

# Check results
echo ""
if [ -f "${OUTPUT_DIR}/bam_snapshots/test_tumor.8-32534767-32536767.png" ]; then
    echo -e "${GREEN}✓ Success! Screenshot generated:${NC}"
    ls -lh "${OUTPUT_DIR}/bam_snapshots/"*.png
    echo ""
    echo "View the screenshot at: ${OUTPUT_DIR}/bam_snapshots/test_tumor.8-32534767-32536767.png"
else
    echo -e "${RED}✗ Error: No screenshot generated${NC}"
    echo "Checking output directory:"
    ls -la "${OUTPUT_DIR}/"
fi