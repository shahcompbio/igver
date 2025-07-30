#!/bin/bash
# Diagnostic script for IGVer Docker container

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}IGVer Docker Diagnostics${NC}"
echo "========================="
echo ""

# Check Docker image
echo -e "${YELLOW}1. Checking Docker image...${NC}"
docker images sahuno/igver:latest

# Check if igver command exists
echo -e "\n${YELLOW}2. Checking if igver command is available...${NC}"
docker run --rm sahuno/igver:latest which igver || echo "igver command not found"

# Check Python and igver module
echo -e "\n${YELLOW}3. Checking Python and igver module...${NC}"
docker run --rm sahuno/igver:latest python -c "import igver; print(f'IGVer version: {igver.__version__}')" || echo "Failed to import igver"

# Check for data module
echo -e "\n${YELLOW}4. Checking for igver.data module...${NC}"
docker run --rm sahuno/igver:latest python -c "from igver.data import *; print('✓ igver.data module found')" || echo "✗ igver.data module not found"

# Check genome_map.yaml
echo -e "\n${YELLOW}5. Checking for genome_map.yaml file...${NC}"
docker run --rm sahuno/igver:latest python -c "
import os
import igver
igver_path = os.path.dirname(igver.__file__)
data_path = os.path.join(igver_path, 'data', 'genome_map.yaml')
if os.path.exists(data_path):
    print(f'✓ genome_map.yaml found at: {data_path}')
    with open(data_path, 'r') as f:
        print('First 5 lines:')
        for i, line in enumerate(f):
            if i < 5:
                print(f'  {line.rstrip()}')
else:
    print(f'✗ genome_map.yaml not found at: {data_path}')
"

# List igver directory structure
echo -e "\n${YELLOW}6. IGVer directory structure in container...${NC}"
docker run --rm sahuno/igver:latest bash -c "find /opt/igver -name '*.py' -o -name '*.yaml' | grep -E '(igver|data)' | sort"

# Check git commit in container
echo -e "\n${YELLOW}7. Git commit in container...${NC}"
docker run --rm sahuno/igver:latest bash -c "cd /opt/igver && git log -1 --oneline"

# Run igver help
echo -e "\n${YELLOW}8. Testing igver help command...${NC}"
docker run --rm sahuno/igver:latest igver --help || echo "Failed to run igver --help"

echo -e "\n${GREEN}Diagnostics complete!${NC}"