#!/bin/bash
# Debug why CLI isn't passing use_singularity correctly

echo "=== Debugging CLI Parameter Passing ==="
echo ""

echo "1. Check if CLI passes use_singularity parameter..."
singularity exec docker://sahuno/igver:latest python -c "
# Check the CLI code
import igver.cli as cli_module
import inspect

# Look at the main function
source = inspect.getsource(cli_module.main)
print('Checking if use_singularity is in kwargs...')
print('Has use_singularity in kwargs?', 'use_singularity' in source)
print('')

# Check what parameters are passed to load_screenshots
lines = source.split('\n')
for i, line in enumerate(lines):
    if 'kwargs = {' in line:
        print(f'Found kwargs at line {i}')
        # Print next 20 lines to see all kwargs
        for j in range(20):
            if i+j < len(lines):
                print(f'  {lines[i+j]}')
            if '}' in lines[i+j] and 'kwargs' in lines[i+j-1]:
                break
"

echo ""
echo "2. Test the workaround directly..."
singularity exec \
    -B "$PWD/test:/data:ro" \
    -B "$PWD/singularity_workaround_output:/output" \
    docker://sahuno/igver:latest \
    igver -i /data/test_tumor.bam -r "8:32534767-32536767" -g hg19 -o /output/ --no-singularity --debug 2>&1 | grep -E "(use_singularity|Running IGV)" | head -10