#!/bin/bash
# Test if auto-detection works without flags

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/auto_detect_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing Auto-Detection ==="
echo ""

# This should work automatically because is_running_in_container() returns True
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python3 -c "
import sys
sys.path.insert(0, '.')

from igver.igver import is_running_in_container, load_screenshots

print('Auto-detection test:')
print('  is_running_in_container():', is_running_in_container())
print('  Should skip Singularity:', is_running_in_container())
print('')

# This should work because use_singularity defaults to not is_running_in_container()
result = load_screenshots(
    paths=['/app/test/test_tumor.bam'],
    regions=['8:32534767-32536767'],
    output_dir='/output/',
    genome='hg19',
    debug=True
)
print('Success!')
"

echo ""
echo "Checking output:"
find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null || echo "No PNG files found"