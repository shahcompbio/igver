#!/bin/bash
# Comprehensive debugging script for IGV screenshot generation failure

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Get absolute paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${PROJECT_DIR}/debug_igv_output"

# Create output directory
mkdir -p "${OUTPUT_DIR}"

echo -e "${GREEN}=== IGV Screenshot Generation Debug ===${NC}"
echo "Project directory: ${PROJECT_DIR}"
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Test 1: Check xvfb installation
echo -e "${YELLOW}1. Checking xvfb installation in container...${NC}"
docker run --rm sahuno/igver:latest which xvfb-run || echo "xvfb-run not found"
docker run --rm sahuno/igver:latest which Xvfb || echo "Xvfb not found"
echo ""

# Test 2: Check IGV installation
echo -e "${YELLOW}2. Checking IGV installation...${NC}"
docker run --rm sahuno/igver:latest ls -la /opt/IGV_2.19.5/igv.sh
docker run --rm sahuno/igver:latest ls -la /opt/IGV_2.19.5/lib/igv.jar
echo ""

# Test 3: Test xvfb directly
echo -e "${YELLOW}3. Testing xvfb display...${NC}"
docker run --rm sahuno/igver:latest bash -c "xvfb-run -a --server-args='-screen 0 1920x1080x24' echo 'Xvfb works'"
echo ""

# Test 4: Run IGVer with verbose output
echo -e "${YELLOW}4. Running IGVer with verbose debugging...${NC}"
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e PYTHONUNBUFFERED=1 \
    sahuno/igver:latest \
    bash -c "cd /opt/igver && python -c \"
import os
import sys
sys.path.insert(0, '/opt/igver')
import igver

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

print('Python path:', sys.path)
print('IGVer location:', igver.__file__)
print('IGV directory:', os.environ.get('IGV_DIR', '/opt/IGV_2.19.5'))

# Try to generate screenshot
try:
    result = igver.load_screenshots(
        bam_paths=['/workspace/test/test_tumor.bam'],
        regions=['8:32534767-32536767'],
        genome='hg19',
        outdir='/output/'
    )
    print('Result:', result)
except Exception as e:
    print('ERROR:', str(e))
    import traceback
    traceback.print_exc()
\""
echo ""

# Test 5: Check for batch script generation
echo -e "${YELLOW}5. Checking batch script generation...${NC}"
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/opt/igver')
from igver import create_batch_script
batch_file = create_batch_script(
    bam_paths=['/workspace/test/test_tumor.bam'],
    regions=['8:32534767-32536767'],
    genome='hg19',
    outdir='/output/'
)
print(f'Batch file created: {batch_file}')
with open(batch_file, 'r') as f:
    print('Batch file contents:')
    print(f.read())
"
echo ""

# Test 6: Try running IGV manually
echo -e "${YELLOW}6. Testing IGV execution manually...${NC}"
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    bash -c "cd /opt/IGV_2.19.5 && xvfb-run -a --server-args='-screen 0 1920x1080x24' java -Xmx750m -jar lib/igv.jar --version 2>&1 || echo 'IGV version check failed'"
echo ""

# Test 7: Check Java
echo -e "${YELLOW}7. Checking Java installation...${NC}"
docker run --rm sahuno/igver:latest java -version
echo ""

# Test 8: Run with strace to see what's failing
echo -e "${YELLOW}8. Running with system call trace (if available)...${NC}"
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    --cap-add SYS_PTRACE \
    sahuno/igver:latest \
    bash -c "if command -v strace &> /dev/null; then
        timeout 30 strace -e trace=execve,open,openat -f igver -i /workspace/test/test_tumor.bam -r '8:32534767-32536767' -g hg19 -o /output/ 2>&1 | grep -E '(igv|xvfb|java)' | head -20
    else
        echo 'strace not available'
    fi"

echo ""
echo -e "${GREEN}Debug complete! Check ${OUTPUT_DIR} for any generated files.${NC}"
ls -la "${OUTPUT_DIR}/" 2>/dev/null || echo "No files generated"