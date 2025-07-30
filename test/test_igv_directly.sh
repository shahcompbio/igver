#!/bin/bash
# Test IGV directly without the Python wrapper

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/direct_igv_test"
mkdir -p "${OUTPUT_DIR}"

echo "=== Direct IGV Test ==="
echo ""

# Create a simple batch file
cat > "${OUTPUT_DIR}/test.batch" << EOF
new
genome hg19
load ${PROJECT_DIR}/test/test_tumor.bam
goto 8:32534767-32536767
snapshot ${OUTPUT_DIR}/direct_test.png
exit
EOF

echo "Batch file created at: ${OUTPUT_DIR}/test.batch"
echo "Contents:"
cat "${OUTPUT_DIR}/test.batch"
echo ""

# Run IGV directly with the batch file
echo "Running IGV directly..."
docker run --rm \
    -v "${PROJECT_DIR}:${PROJECT_DIR}:ro" \
    -v "${OUTPUT_DIR}:${OUTPUT_DIR}" \
    sahuno/igver:latest \
    bash -c "cd /opt/IGV_2.19.5 && xvfb-run -a --server-args='-screen 0 1920x1080x24' timeout 60 java -Xmx750m -jar lib/igv.jar -b ${OUTPUT_DIR}/test.batch"

echo ""
echo "Checking for output:"
ls -la "${OUTPUT_DIR}/"

if [ -f "${OUTPUT_DIR}/direct_test.png" ]; then
    echo "SUCCESS: IGV generated the screenshot!"
    echo "Size: $(stat -c%s "${OUTPUT_DIR}/direct_test.png") bytes"
else
    echo "FAILED: No screenshot generated"
    # Check for IGV log
    if [ -f "${OUTPUT_DIR}/igv.log" ]; then
        echo "IGV log:"
        cat "${OUTPUT_DIR}/igv.log"
    fi
fi