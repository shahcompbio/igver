#!/bin/bash
# Test IGV using the igv.sh wrapper script

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/wrapper_igv_test"
mkdir -p "${OUTPUT_DIR}"

echo "=== IGV Test with Wrapper Script ==="
echo ""

# Create a simple batch file
cat > "${OUTPUT_DIR}/test.batch" << EOF
new
genome hg19
load ${PROJECT_DIR}/test/test_tumor.bam
goto 8:32534767-32536767
snapshot ${OUTPUT_DIR}/wrapper_test.png
exit
EOF

echo "Batch file created"
echo ""

# Method 1: Use igv.sh wrapper
echo "Method 1: Using igv.sh wrapper..."
docker run --rm \
    -v "${PROJECT_DIR}:${PROJECT_DIR}:ro" \
    -v "${OUTPUT_DIR}:${OUTPUT_DIR}" \
    sahuno/igver:latest \
    bash -c "cd /opt/IGV_2.19.5 && xvfb-run -a --server-args='-screen 0 1920x1080x24' timeout 60 ./igv.sh -b ${OUTPUT_DIR}/test.batch"

echo ""
echo "Checking for output:"
ls -la "${OUTPUT_DIR}/"

# Method 2: Set classpath manually
echo ""
echo "Method 2: Setting classpath manually..."
docker run --rm \
    -v "${PROJECT_DIR}:${PROJECT_DIR}:ro" \
    -v "${OUTPUT_DIR}:${OUTPUT_DIR}" \
    sahuno/igver:latest \
    bash -c "
cd /opt/IGV_2.19.5
# Build classpath from all jars in lib directory
CLASSPATH=\$(find lib -name '*.jar' | tr '\n' ':')
echo 'Classpath has \$(echo \$CLASSPATH | tr ':' '\n' | wc -l) jar files'

# Run IGV with full classpath
xvfb-run -a --server-args='-screen 0 1920x1080x24' timeout 60 \
    java -Xmx750m -cp \"\$CLASSPATH\" org.broad.igv.ui.Main -b ${OUTPUT_DIR}/test.batch
"

if [ -f "${OUTPUT_DIR}/wrapper_test.png" ]; then
    echo "SUCCESS: Screenshot generated!"
else
    echo "FAILED: No screenshot found"
fi