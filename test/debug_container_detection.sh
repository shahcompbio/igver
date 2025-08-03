#!/bin/bash
# Debug why container detection isn't working inside Docker

echo "=== Debugging Container Detection in Docker ==="
echo ""

# Check what the container sees
echo "1. Checking container environment..."
docker run --rm sahuno/igver:latest bash -c "
echo 'Checking /.dockerenv:'
ls -la /.dockerenv 2>/dev/null || echo '  /.dockerenv not found'
echo ''
echo 'Checking /proc/1/cgroup:'
cat /proc/1/cgroup | head -5
echo ''
echo 'Environment variables:'
env | grep -E 'IGVER|SINGULARITY|DOCKER' || echo '  No relevant env vars found'
"

echo ""
echo "2. Testing detection with mounted code..."
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
docker run --rm \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -e PYTHONPATH=/opt/igver \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/opt/igver')
from igver.igver import is_running_in_container
import os

print('Container detection result:', is_running_in_container())
print('')
print('Debug info:')
print('  /.dockerenv exists:', os.path.exists('/.dockerenv'))
print('  IGVER_IN_CONTAINER:', os.environ.get('IGVER_IN_CONTAINER', 'not set'))

# Check cgroup
try:
    with open('/proc/1/cgroup', 'r') as f:
        content = f.read()
        print('  /proc/1/cgroup contains docker:', 'docker' in content)
        print('  First few lines of /proc/1/cgroup:')
        for line in content.split('\n')[:3]:
            print('    ', line)
except Exception as e:
    print('  Error reading /proc/1/cgroup:', e)
"

echo ""
echo "3. Checking if IGVER_IN_CONTAINER is set in the image..."
docker run --rm sahuno/igver:latest env | grep IGVER || echo "IGVER_IN_CONTAINER not found in environment"