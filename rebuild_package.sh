#!/bin/bash
# Script to rebuild IGVer package with data files fix

echo "Rebuilding IGVer package with data files..."

# Clean up old builds
echo "Cleaning old builds..."
rm -rf build/ dist/ igver.egg-info/

# Reinstall in development mode
echo "Installing package in development mode..."
pip install -e .

# Build distribution packages
echo "Building distribution packages..."
python setup.py sdist bdist_wheel

# Test the import
echo "Testing package import..."
python -c "import igver; print('IGVer version:', igver.__version__)"
python -c "from igver.data import *; print('Data module loaded successfully')"

# Show package contents
echo "Package contents:"
tar -tzf dist/igver-*.tar.gz | grep -E "(data|yaml)" | head -10

echo "Package rebuild complete!"
echo ""
echo "To rebuild the Singularity container, run:"
echo "  singularity build --remote igver_fixed.sif docker://sahuno/igver:latest"
echo ""
echo "Or if you have a local Dockerfile:"
echo "  docker build -t igver:fixed ."
echo "  singularity build igver_fixed.sif docker-daemon://igver:fixed"