#!/bin/bash
# Working test script with correct API

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/working_test_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== IGVer Docker Test with Correct API ==="
echo "Output directory: ${OUTPUT_DIR}"
echo ""

# Test 1: Direct Python API call with correct parameters
echo "1. Testing IGVer Python API directly..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/opt/igver')
import igver

# Test with correct API
result = igver.load_screenshots(
    paths=['/workspace/test/test_tumor.bam'],
    regions=['8:32534767-32536767'],
    output_dir='/output/',
    genome='hg19',
    debug=True
)
print('Result:', result)
"

echo ""
echo "2. Testing create_batch_script with correct parameters..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/opt/igver')
from igver import create_batch_script

# Check function signature
import inspect
print('create_batch_script signature:', inspect.signature(create_batch_script))

# Try with correct parameters
batch_file = create_batch_script(
    paths=['/workspace/test/test_tumor.bam'],
    regions=['8:32534767-32536767'],
    genome='hg19',
    output_dir='/output/'
)
print('Batch file:', batch_file)
with open(batch_file, 'r') as f:
    print('Contents:')
    print(f.read())
"

echo ""
echo "3. Testing CLI with correct syntax..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    igver -i /workspace/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --debug

echo ""
echo "4. Checking output directory:"
ls -la "${OUTPUT_DIR}/" 2>/dev/null || echo "No output directory"
find "${OUTPUT_DIR}" -name "*.png" -o -name "*.log" -o -name "*.batch" 2>/dev/null || echo "No files found"