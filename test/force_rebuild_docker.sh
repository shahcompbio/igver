#!/bin/bash
# Force complete rebuild of Docker image

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Force rebuilding IGVer Docker image...${NC}"

# Change to docker directory
cd docker/

# Remove any existing images
echo -e "${YELLOW}Removing existing sahuno/igver images...${NC}"
docker rmi sahuno/igver:latest sahuno/igver:2.19.5 || true

# Pull latest base image
echo -e "${YELLOW}Pulling latest base image...${NC}"
docker pull archlinux:latest

# Build with absolutely no cache and a unique build arg to force fresh git clone
echo -e "${YELLOW}Building with --no-cache and unique build arg...${NC}"
TIMESTAMP=$(date +%s)
docker build --no-cache --build-arg CACHE_BUST=${TIMESTAMP} -t sahuno/igver:latest .

# Tag with version
echo -e "${YELLOW}Tagging as 2.19.5...${NC}"
docker tag sahuno/igver:latest sahuno/igver:2.19.5

# Test the build
echo -e "${GREEN}Testing the new build...${NC}"
docker run --rm sahuno/igver:latest python -c "from igver.data import *; print('✓ igver.data module loaded successfully')"

echo -e "${GREEN}Build complete! Now push with:${NC}"
echo "  docker push sahuno/igver:latest"
echo "  docker push sahuno/igver:2.19.5"