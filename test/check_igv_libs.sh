#!/bin/bash
# Check IGV libraries and classpath

echo "=== Checking IGV Installation ==="
echo ""

# Check IGV directory structure
echo "1. IGV directory contents:"
docker run --rm sahuno/igver:latest ls -la /opt/IGV_2.19.5/

echo ""
echo "2. IGV lib directory:"
docker run --rm sahuno/igver:latest ls -la /opt/IGV_2.19.5/lib/ | head -20

echo ""
echo "3. Checking for htsjdk:"
docker run --rm sahuno/igver:latest find /opt/IGV_2.19.5 -name "*htsjdk*" -o -name "*tribble*"

echo ""
echo "4. Checking igv.sh script:"
docker run --rm sahuno/igver:latest cat /opt/IGV_2.19.5/igv.sh

echo ""
echo "5. Testing IGV with igv.sh script:"
docker run --rm sahuno/igver:latest bash -c "cd /opt/IGV_2.19.5 && xvfb-run -a ./igv.sh --version 2>&1" || echo "Failed"

echo ""
echo "6. Checking Java classpath in igv.sh:"
docker run --rm sahuno/igver:latest bash -c "cd /opt/IGV_2.19.5 && grep -E 'classpath|CLASSPATH|java' igv.sh"