#!/bin/bash
# Verify that our updated code is being loaded

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Verifying Code Loading ==="
echo ""

# 1. Check if our is_running_in_container function exists
echo "1. Checking if our updated code is being loaded..."
docker run --rm \
    -v "${PROJECT_DIR}/igver:/opt/igver/igver:ro" \
    -e PYTHONPATH=/opt/igver \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python -c "
import sys
print('Python path:', sys.path[:3])
print('')

# Try to import and check our function
try:
    from igver.igver import is_running_in_container
    print('✓ is_running_in_container function found')
    print('  Result:', is_running_in_container())
    
    # Check the function source
    import inspect
    source = inspect.getsource(is_running_in_container)
    print('  Function first few lines:')
    for line in source.split('\\n')[:5]:
        print('   ', line)
except Exception as e:
    print('✗ Error importing:', e)

print('')
print('Checking what igver module is loaded:')
import igver
print('  igver location:', igver.__file__)
import igver.igver as igver_module
print('  igver.igver location:', igver_module.__file__)

# Check if run_igv has use_singularity parameter
import inspect
sig = inspect.signature(igver_module.run_igv)
print('  run_igv parameters:', list(sig.parameters.keys()))
print('  Has use_singularity?', 'use_singularity' in sig.parameters)
"

echo ""
echo "2. Let's check what's in the container's original igver..."
docker run --rm sahuno/igver:latest python -c "
import igver.igver as igver_module
import inspect
sig = inspect.signature(igver_module.run_igv)
print('Container original run_igv parameters:', list(sig.parameters.keys()))
"

echo ""
echo "3. Force using our local igver module directly..."
docker run --rm \
    -v "${PROJECT_DIR}:/local_code:ro" \
    -e PYTHONPATH=/local_code \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python -c "
import sys
sys.path.insert(0, '/local_code')
print('Python path:', sys.path[:3])

from igver.igver import is_running_in_container, run_igv
print('is_running_in_container():', is_running_in_container())

import inspect
sig = inspect.signature(run_igv)
print('run_igv parameters:', list(sig.parameters.keys()))
"