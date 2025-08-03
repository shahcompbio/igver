#!/bin/bash
# Force use of local code by uninstalling container's igver

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/force_local_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Force Local Code Test ==="
echo ""

# Run with local code, but first uninstall the container's version
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    bash -c "
# Show what's installed
echo 'Installed igver:'
pip show igver || echo 'Not found with pip'
echo ''

# Run with our local code
echo 'Running with local code...'
python3 -c \"
import sys
import os

# Force our local code to be first
sys.path.insert(0, '/app')
os.environ['IGVER_IN_CONTAINER'] = '1'

# Now import and run
from igver.igver import is_running_in_container, load_screenshots
print('Container detected:', is_running_in_container())
print('Starting screenshot generation...')

try:
    result = load_screenshots(
        paths=['/app/test/test_tumor.bam'],
        regions=['8:32534767-32536767'],
        output_dir='/output/',
        genome='hg19',
        debug=True,
        use_singularity=False  # Force no singularity
    )
    print('Success! Result:', result)
except Exception as e:
    print('Error:', e)
    import traceback
    traceback.print_exc()
\"
"

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/"
find "${OUTPUT_DIR}" -name "*.png" -type f 2>/dev/null || echo "No PNG files found"