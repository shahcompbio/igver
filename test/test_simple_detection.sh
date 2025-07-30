#!/bin/bash
# Simple test to verify our code is working

echo "=== Testing Container Detection Directly ==="
echo ""

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Test 1: Direct Python test
echo "1. Testing is_running_in_container directly..."
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python3 -c "
import sys
print('sys.path:', sys.path[:2])

# Import directly from our file
sys.path.insert(0, '.')
from igver.igver import is_running_in_container

print('is_running_in_container():', is_running_in_container())
print('Expected: True')
"

echo ""
echo "2. Let's trace the execution..."
docker run --rm \
    -v "${PROJECT_DIR}:/app:ro" \
    -w /app \
    -e PYTHONPATH=/app \
    -e IGVER_IN_CONTAINER=1 \
    sahuno/igver:latest \
    python3 -c "
import sys
sys.path.insert(0, '.')

# Add debug prints to see what's happening
print('=== Debug Trace ===')
print('Python executable:', sys.executable)
print('Python version:', sys.version.split()[0])

# Import and check
try:
    import igver.igver as igver_module
    print('igver module loaded from:', igver_module.__file__)
    
    # Check if our function exists
    if hasattr(igver_module, 'is_running_in_container'):
        print('✓ is_running_in_container found')
        result = igver_module.is_running_in_container()
        print('  Result:', result)
    else:
        print('✗ is_running_in_container NOT found')
        
    # Check run_igv signature
    import inspect
    if hasattr(igver_module, 'run_igv'):
        sig = inspect.signature(igver_module.run_igv)
        params = list(sig.parameters.keys())
        print('run_igv parameters:', params)
        print('Has use_singularity?', 'use_singularity' in params)
except Exception as e:
    import traceback
    print('Error:', e)
    traceback.print_exc()
"

echo ""
echo "3. Check what Python igver is using..."
docker run --rm sahuno/igver:latest which python
docker run --rm sahuno/igver:latest python --version