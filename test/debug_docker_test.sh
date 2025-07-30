#!/bin/bash
# Debug test for IGVer Docker container

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TEST_BAM="${SCRIPT_DIR}/test/test_tumor.bam"
OUTPUT_DIR="${SCRIPT_DIR}/debug_docker_output"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}Debug Docker test of IGVer...${NC}"
echo ""

# Test 1: Check if BAM file is accessible
echo -e "${YELLOW}1. Testing BAM file access...${NC}"
docker run --rm \
    -v "${SCRIPT_DIR}:/app:ro" \
    sahuno/igver:latest \
    ls -la /app/test/test_tumor.bam*

# Test 2: Run with debug flag
echo -e "\n${YELLOW}2. Running IGVer with debug flag...${NC}"
docker run --rm \
    -v "${SCRIPT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /app/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --debug

# Test 3: Check output directory
echo -e "\n${YELLOW}3. Checking output directory...${NC}"
echo "Contents of ${OUTPUT_DIR}:"
ls -la "${OUTPUT_DIR}/"

# Test 4: Check for any error logs
echo -e "\n${YELLOW}4. Checking for IGV logs...${NC}"
if [ -d "${OUTPUT_DIR}/igv_logs" ]; then
    echo "IGV logs found:"
    ls -la "${OUTPUT_DIR}/igv_logs/"
    if [ -f "${OUTPUT_DIR}/igv_logs/igv.log" ]; then
        echo "Last 20 lines of igv.log:"
        tail -20 "${OUTPUT_DIR}/igv_logs/igv.log"
    fi
else
    echo "No IGV logs directory found"
fi

# Test 5: Try running IGV directly
echo -e "\n${YELLOW}5. Testing IGV directly in container...${NC}"
docker run --rm \
    sahuno/igver:latest \
    bash -c "cd /opt/IGV_2.19.5 && ls -la igv.sh"

echo -e "\n${GREEN}Debug test complete!${NC}"