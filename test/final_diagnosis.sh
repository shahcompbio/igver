#!/bin/bash
# Final diagnosis of the parameter passing issue

echo "=== Final Diagnosis ==="
echo ""

# Check if the Docker image has the updated CLI code
echo "Checking CLI code in Docker image..."
singularity exec docker://sahuno/igver:latest python -c "
import igver.cli as cli
import inspect

# Get the source of main function
source = inspect.getsource(cli.main)

# Check if use_singularity is in kwargs
if '\"use_singularity\"' in source:
    print('✓ CLI has use_singularity in kwargs')
    # Find the line
    for i, line in enumerate(source.split('\n')):
        if 'use_singularity' in line:
            print(f'  Line {i}: {line.strip()}')
else:
    print('✗ CLI does NOT have use_singularity in kwargs')
    print('  This explains why auto-detection fails!')
"

echo ""
echo "Checking git history..."
cd /home/sahuno/apps/igver
echo "Last commit:"
git log -1 --oneline

echo ""
echo "Files changed in last commit:"
git show --name-only HEAD

echo ""
echo "Check if cli.py was included:"
git show HEAD | grep -A5 -B5 "use_singularity.*not args.no_singularity" || echo "CLI changes not found in last commit"