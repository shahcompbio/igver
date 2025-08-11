#!/bin/bash
# Working Singularity test with --no-singularity flag

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/singularity_working_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Singularity Test with --no-singularity Flag ==="
echo ""

# This should definitely work
echo "Running with --no-singularity flag..."
singularity exec \
    -B "${PROJECT_DIR}/test:/data:ro" \
    -B "${OUTPUT_DIR}:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --no-singularity

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/"

if [ -f "${OUTPUT_DIR}/bam_snapshots/test_tumor.8-32534767-32536767.png" ]; then
    echo ""
    echo "SUCCESS! Screenshot generated using Singularity."
    echo ""
    echo "For now, use the --no-singularity flag when running with Singularity:"
    echo "  singularity exec docker://sahuno/igver:latest igver ... --no-singularity"
else
    find "${OUTPUT_DIR}" -name "*.png" -type f
fi