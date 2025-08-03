# IGVer Container Fix Plan

## Problem Summary
The IGVer tool was designed to run IGV inside a Singularity container. However, when running IGVer inside a Docker container, it attempts to execute `singularity` commands, which fail because:
1. Singularity is not installed inside the Docker container
2. Running nested containers (Docker → Singularity) is complex and unnecessary
3. IGV is already installed and available inside the Docker container

## Root Cause
In `igver/igver.py`, the `run_igv()` function always wraps the IGV command with singularity:
```python
cmd = f'xvfb-run --auto-display --server-args="-screen 0 1920x1080x24" {igv_runfile} -b {batch_script} --igvDirectory {igv_dir}'
cmd = f'singularity run {singularity_args} {singularity_image} {cmd}'  # This fails in Docker
```

## Solution Overview
Modify the code to detect when it's already running inside a container and skip the Singularity wrapper in those cases.

## Implementation Plan

### 1. Add Container Detection (Priority: High)
- Add a function to detect if we're running inside a container
- Check for Docker/Singularity-specific files or environment variables
- Support override via environment variable

### 2. Modify run_igv() Function (Priority: High)
- Add conditional logic to skip Singularity wrapper when in container
- Preserve all other functionality
- Maintain backward compatibility for non-container usage

### 3. Update CLI Arguments (Priority: Medium)
- Add `--no-singularity` flag for explicit control
- Update help text to explain container usage

### 4. Environment Variables (Priority: High)
- `IGVER_IN_CONTAINER`: Set to "1" to indicate running in container
- `IGVER_NO_SINGULARITY`: Alternative way to disable Singularity wrapper
- Document these in README

### 5. Testing (Priority: High)
- Test in Docker container
- Test with native installation + Singularity
- Test all command-line options
- Verify screenshot generation works

### 6. Documentation Updates (Priority: Medium)
- Update README with Docker usage instructions
- Add troubleshooting section
- Document environment variables

### 7. Docker Image Update (Priority: High)
- Set appropriate environment variables in Dockerfile
- Rebuild and push updated image
- Tag with new version

## Code Changes Required

### File: `igver/igver.py`

1. Add container detection function:
```python
def is_running_in_container():
    """Detect if running inside a container (Docker or Singularity)"""
    # Check environment variable first
    if os.environ.get('IGVER_IN_CONTAINER', '').strip() == '1':
        return True
    if os.environ.get('IGVER_NO_SINGULARITY', '').strip() == '1':
        return True
    
    # Check for Docker
    if os.path.exists('/.dockerenv'):
        return True
    
    # Check for Singularity
    if os.environ.get('SINGULARITY_CONTAINER'):
        return True
    
    # Check cgroup for docker/lxc
    try:
        with open('/proc/1/cgroup', 'r') as f:
            if 'docker' in f.read() or 'lxc' in f.read():
                return True
    except:
        pass
    
    return False
```

2. Modify `run_igv()` function to use detection:
```python
def run_igv(batch_script, png_paths, igv_dir="/opt/IGV_2.19.5", overwrite=False, 
            singularity_image='docker://sahuno/igver:latest', singularity_args='-B /data1 -B /home',
            debug=False, use_singularity=None):
    
    # Auto-detect if we should use singularity
    if use_singularity is None:
        use_singularity = not is_running_in_container()
    
    # Build IGV command
    igv_runfile = os.path.join(igv_dir, "igv.sh")
    cmd = f'xvfb-run --auto-display --server-args="-screen 0 1920x1080x24" {igv_runfile} -b {batch_script}'
    
    # Only wrap with singularity if needed
    if use_singularity:
        cmd = f'singularity run {singularity_args} {singularity_image} {cmd}'
        if debug:
            print(f"[LOG:{time.ctime()}] Running IGV with Singularity")
    else:
        if debug:
            print(f"[LOG:{time.ctime()}] Running IGV directly (container mode)")
    
    # ... rest of function remains the same
```

### File: `igver/cli.py`

1. Add command-line argument:
```python
parser.add_argument('--no-singularity', action='store_true',
                    help='Run IGV directly without Singularity wrapper (auto-detected in containers)')
```

2. Pass the flag to load_screenshots:
```python
figures = igver.load_screenshots(
    # ... other args ...
    use_singularity=not args.no_singularity
)
```

### File: `docker/Dockerfile`

Add environment variable:
```dockerfile
# Set environment to indicate we're in a container
ENV IGVER_IN_CONTAINER=1
```

## Success Criteria
1. ✓ Docker users can run `igver` command without errors
2. ✓ Screenshots are generated successfully
3. ✓ Existing Singularity-based workflows continue to work
4. ✓ Clear documentation for both usage modes
5. ✓ Automated detection works reliably

## Timeline
1. Implement code changes: 30 minutes
2. Test thoroughly: 30 minutes
3. Update documentation: 15 minutes
4. Rebuild and push Docker image: 15 minutes

Total estimated time: ~1.5 hours