#!/bin/bash
# Run IGVer directly with our local code

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/direct_run_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Direct Run with Local Code ==="
echo ""

# Run directly from our local code
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python -m igver.cli -i /app/test/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --debug

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/"

if [ -f "${OUTPUT_DIR}/bam_snapshots/test_tumor.8-32534767-32536767.png" ]; then
    echo "SUCCESS! Screenshot generated."
else
    echo "Failed. Checking for any PNG files..."
    find "${OUTPUT_DIR}" -name "*.png" -type f
fi