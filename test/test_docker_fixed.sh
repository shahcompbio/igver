#!/bin/bash
# Test IGVer with environment variable to skip singularity

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${PROJECT_DIR}/fixed_docker_output"
mkdir -p "${OUTPUT_DIR}"

echo "=== Testing IGVer with Container Fix ==="
echo ""

# The issue: The code tries to run singularity inside Docker
# Solution: We need to modify the code to detect if we're already in a container

# Test 1: Check if we can set an environment variable to bypass singularity
echo "1. Testing with IGVER_CONTAINER environment variable..."
docker run --rm \
    -v "${PROJECT_DIR}:/workspace:ro" \
    -v "${OUTPUT_DIR}:/output" \
    -e IGVER_CONTAINER=1 \
    sahuno/igver:latest \
    python -c "
import os
import sys
sys.path.insert(0, '/opt/igver')

# Monkey patch the run_igv function to skip singularity when in container
import igver.igver as igver_module

original_run_igv = igver_module.run_igv

def patched_run_igv(batch_script, png_paths, igv_dir='/opt/IGV_2.19.5', overwrite=False, 
                    singularity_image='docker://sahuno/igver:latest', singularity_args='-B /data1 -B /home',
                    debug=True):
    # If we're in a container, run IGV directly without singularity
    import subprocess
    import time
    import os
    
    igv_runfile = os.path.join(igv_dir, 'igv.sh')
    cmd = f'xvfb-run --auto-display --server-args=\"-screen 0 1920x1080x24\" {igv_runfile} -b {batch_script}'
    
    print(f'[LOG:{time.ctime()}] Running IGV command (container mode):\\n{cmd}')
    
    n_iter = 0
    max_iterations = 2
    
    while n_iter < max_iterations:
        print(f'[LOG:{time.ctime()}] Iteration #{n_iter + 1}: Ensuring PNG files exist')
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print(f'[STDOUT:{time.ctime()}]\\n{result.stdout.decode()}')
        print(f'[STDERR:{time.ctime()}]\\n{result.stderr.decode()}')
        
        # Check if all PNG files exist
        all_exist = all(os.path.exists(png_path) for png_path in png_paths)
        if all_exist:
            print(f'[LOG:{time.ctime()}] All PNG files generated successfully')
            return
        
        n_iter += 1
        time.sleep(2)
    
    raise RuntimeError(f'[ERROR:{time.ctime()}] Failed to generate all PNG files after {max_iterations} iterations.')

# Apply the patch
igver_module.run_igv = patched_run_igv

# Now run the test
import igver
result = igver.load_screenshots(
    paths=['/workspace/test/test_tumor.bam'],
    regions=['8:32534767-32536767'],
    output_dir='/output/',
    genome='hg19',
    debug=True
)
print('Result:', result)
"

echo ""
echo "Checking output:"
ls -la "${OUTPUT_DIR}/" 2>/dev/null || echo "No files generated"
find "${OUTPUT_DIR}" -name "*.png" 2>/dev/null || echo "No PNG files found"