#!/bin/bash
# Test if IGV is timing out

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/timeout_test_output"
mkdir -p "${OUTPUT_DIR}"

echo "Testing IGV with extended timeout..."

# Run with extended timeout and watch for output
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    sahuno/igver:latest \
    bash -c "
# Modify the IGV timeout
export IGV_TIMEOUT=120

# Run IGVer with debug output
python -c \"
import os
import subprocess
import time

print('Starting IGV test with extended timeout...')
print('IGV will have 120 seconds to generate screenshots')

# Create a simple batch file
batch_content = '''new
genome hg19
load /workspace/test/test_tumor.bam
goto 8:32534767-32536767
snapshot /output/test_screenshot.png
exit
'''

with open('/tmp/test.batch', 'w') as f:
    f.write(batch_content)

print('Batch file created. Starting IGV...')

# Run IGV with xvfb
cmd = [
    'xvfb-run', '-a', '--server-args=-screen 0 1920x1080x24',
    'java', '-Xmx750m', '-jar', '/opt/IGV_2.19.5/lib/igv.jar',
    '-b', '/tmp/test.batch'
]

print('Command:', ' '.join(cmd))
start_time = time.time()

try:
    # Run with timeout
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    elapsed = time.time() - start_time
    print(f'IGV completed in {elapsed:.1f} seconds')
    print('STDOUT:', result.stdout)
    print('STDERR:', result.stderr)
    print('Return code:', result.returncode)
except subprocess.TimeoutExpired:
    elapsed = time.time() - start_time
    print(f'IGV timed out after {elapsed:.1f} seconds')
except Exception as e:
    print(f'Error: {e}')

# Check if screenshot was created
if os.path.exists('/output/test_screenshot.png'):
    print('SUCCESS: Screenshot created!')
    print(f'Size: {os.path.getsize(\"/output/test_screenshot.png\")} bytes')
else:
    print('FAILED: No screenshot generated')
    print('Contents of /output:')
    os.system('ls -la /output/')
\"
"

echo ""
echo "Checking output directory:"
ls -la "${OUTPUT_DIR}/"