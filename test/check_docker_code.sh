#!/bin/bash
# Check what code is in the Docker image

echo "=== Checking Code in Docker Image ==="
echo ""

echo "1. Check if run_igv has use_singularity parameter..."
singularity exec docker://sahuno/igver:latest python -c "
import igver.igver as igver_module
import inspect

# Check run_igv signature
sig = inspect.signature(igver_module.run_igv)
params = list(sig.parameters.keys())
print('run_igv parameters:', params)
print('Has use_singularity?', 'use_singularity' in params)

# Check if the auto-detection logic is there
source = inspect.getsource(igver_module.run_igv)
print('')
print('Has auto-detection logic?', 'if use_singularity is None:' in source)
print('Has container check?', 'is_running_in_container' in source)
"

echo ""
echo "2. Check the actual run_igv code..."
singularity exec docker://sahuno/igver:latest python -c "
import igver.igver as igver_module
import inspect

# Get the run_igv source
source = inspect.getsource(igver_module.run_igv)
# Find the relevant part
lines = source.split('\n')
for i, line in enumerate(lines):
    if 'use_singularity is None' in line or 'Only wrap with singularity' in line:
        print(f'Line {i}: {line}')
        if i < len(lines) - 3:
            print(f'Line {i+1}: {lines[i+1]}')
            print(f'Line {i+2}: {lines[i+2]}')
            print(f'Line {i+3}: {lines[i+3]}')
        print()
"