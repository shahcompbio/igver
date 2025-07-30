#!/bin/bash
# Test the CLI with our fixes

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/cli_test_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing CLI with Container Fix ==="
echo ""

# Test the CLI directly
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    bash -c "
# First check if the CLI has our changes
echo 'Checking CLI for --no-singularity flag...'
python -m igver.cli --help | grep -A1 'no-singularity' || echo 'Flag not found'
echo ''

# Now run with the flag
echo 'Running with --no-singularity flag...'
python -m igver.cli -i /app/test/test_tumor.bam -r '8:32534767-32536767' -g hg19 -o /output/ --no-singularity --debug
"

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/"
find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null || echo "No PNG files found"