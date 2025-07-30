#!/bin/bash
# Script to build and push IGVer Docker image to Docker Hub with logging

set -e  # Exit on error

# Log file
LOG_FILE="docker_build_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Start logging
{
echo "Docker Build Log - $(date)"
echo "========================="
echo ""

echo -e "${GREEN}Building IGVer Docker image...${NC}"

# Change to docker directory
cd docker/

# Build the Docker image (--no-cache ensures fresh git clone)
echo -e "${YELLOW}Building docker image: sahuno/igver:latest${NC}"
echo -e "${YELLOW}Using --no-cache to ensure latest code from GitHub${NC}"
docker build --no-cache -t sahuno/igver:latest . 2>&1

# Tag with IGV version
IGV_VERSION="2.19.5"
echo -e "${YELLOW}Tagging with IGV version: sahuno/igver:${IGV_VERSION}${NC}"
docker tag sahuno/igver:latest sahuno/igver:${IGV_VERSION}

# Tag with additional version if specified
if [ ! -z "$1" ]; then
    VERSION=$1
    echo -e "${YELLOW}Also tagging as: sahuno/igver:${VERSION}${NC}"
    docker tag sahuno/igver:latest sahuno/igver:${VERSION}
fi

# Test the image
echo -e "${GREEN}Testing Docker image...${NC}"
docker run --rm sahuno/igver:latest igver --help 2>&1

# Push to Docker Hub
echo -e "${GREEN}Pushing to Docker Hub...${NC}"
echo -e "${YELLOW}Make sure you're logged in to Docker Hub (docker login)${NC}"

docker push sahuno/igver:latest 2>&1
docker push sahuno/igver:${IGV_VERSION} 2>&1

if [ ! -z "$1" ]; then
    docker push sahuno/igver:${VERSION} 2>&1
    echo -e "${GREEN}Pushed tags: :latest, :${IGV_VERSION}, and :${VERSION}${NC}"
else
    echo -e "${GREEN}Pushed tags: :latest and :${IGV_VERSION}${NC}"
fi

echo -e "${GREEN}Docker image successfully built and pushed!${NC}"
echo ""
echo "Users can now use the image with:"
echo "  Docker: docker run -v /path/to/data:/data sahuno/igver:latest igver -i /data/sample.bam -r \"chr1:1000-2000\" -o /data/output"
echo "  Singularity: singularity exec docker://sahuno/igver:latest igver -i sample.bam -r \"chr1:1000-2000\" -o output/"

echo ""
echo "Build completed at $(date)"
} | tee "$LOG_FILE"

echo ""
echo "Full log saved to: $LOG_FILE"