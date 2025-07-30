# Docker Usage Guide for IGVer

## Quick Start

```bash
# Basic usage with Docker
docker run --rm \
    -v /path/to/your/data:/data:ro \
    -v /path/to/output:/output \
    sahuno/igver:latest \
    igver -i /data/sample.bam -r "chr1:1000000-2000000" -g hg19 -o /output/
```

## Container vs Native Usage

IGVer was originally designed to run IGV inside a Singularity container. When using the Docker image, IGVer automatically detects it's running in a container and skips the Singularity wrapper.

### Auto-Detection
The tool automatically detects when it's running inside a container by checking:
- Docker-specific files (/.dockerenv)
- Environment variables (IGVER_IN_CONTAINER, SINGULARITY_CONTAINER)
- Process information (/proc/1/cgroup)

### Manual Control
You can manually control the behavior using:
- `--no-singularity` flag: Forces IGVer to run without Singularity
- `IGVER_IN_CONTAINER=1` environment variable: Tells IGVer it's in a container
- `IGVER_NO_SINGULARITY=1` environment variable: Disables Singularity wrapper

## Examples

### Single BAM, Single Region
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    sahuno/igver:latest \
    igver -i /workspace/sample.bam -r "chr1:1000000-2000000" -o /output/
```

### Multiple BAMs, Multiple Regions
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    sahuno/igver:latest \
    igver -i /workspace/tumor.bam /workspace/normal.bam \
          -r "chr1:1000000-2000000" "chr2:3000000-4000000" \
          -g hg38 -o /output/
```

### Using BED File for Regions
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    sahuno/igver:latest \
    igver -i /workspace/sample.bam \
          -r /workspace/regions.bed \
          -g hg19 -o /output/
```

### With Debug Output
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    sahuno/igver:latest \
    igver -i /workspace/sample.bam \
          -r "chr1:1000000-2000000" \
          -o /output/ --debug
```

### Custom Genome
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    sahuno/igver:latest \
    igver -i /workspace/sample.bam \
          -r "chr1:1000000-2000000" \
          -g mm39 -o /output/
```

## Volume Mounting

### Important Notes:
1. **Input files must be mounted**: Use `-v` to mount directories containing your BAM files
2. **Output directory must be mounted**: Mount a directory for output screenshots
3. **Use absolute paths**: Docker requires absolute paths for volume mounts
4. **Read-only for input**: Use `:ro` flag for input data to prevent accidental modification

### Example Directory Structure:
```
/home/user/project/
├── data/
│   ├── sample1.bam
│   ├── sample1.bam.bai
│   ├── sample2.bam
│   └── sample2.bam.bai
├── regions.bed
└── output/
```

Mount command:
```bash
docker run --rm \
    -v /home/user/project:/project:ro \
    -v /home/user/project/output:/output \
    sahuno/igver:latest \
    igver -i /project/data/sample1.bam \
          -r /project/regions.bed \
          -o /output/
```

## Environment Variables

- `IGVER_IN_CONTAINER=1`: Set automatically in Docker image
- `IGVER_IMAGE`: Override default Singularity image (not used in Docker)

## Troubleshooting

### No Screenshots Generated
- Check if BAM files have index files (.bai)
- Verify chromosome names match the reference genome
- Use `--debug` flag for detailed output

### Permission Denied
- Ensure output directory is writable
- Check Docker daemon permissions
- Try running with `sudo` if needed

### File Not Found
- Use absolute paths for volume mounts
- Verify files exist at the mounted locations
- Check file paths inside container match your volume mounts

### Memory Issues
- IGV uses up to 750MB by default
- For large regions or many tracks, increase Docker memory limit:
  ```bash
  docker run --rm -m 2g ...
  ```

## Advanced Usage

### Custom IGV Settings
Create a custom IGV preferences file and mount it:
```bash
docker run --rm \
    -v $(pwd):/workspace:ro \
    -v $(pwd)/output:/output \
    -v $(pwd)/igv_prefs.xml:/igv_prefs.xml:ro \
    sahuno/igver:latest \
    igver -i /workspace/sample.bam \
          -r "chr1:1000000-2000000" \
          -c /igv_prefs.xml \
          -o /output/
```

### Batch Processing
Create a script to process multiple samples:
```bash
#!/bin/bash
for bam in data/*.bam; do
    name=$(basename "$bam" .bam)
    docker run --rm \
        -v $(pwd):/workspace:ro \
        -v $(pwd)/output/$name:/output \
        sahuno/igver:latest \
        igver -i /workspace/$bam \
              -r /workspace/regions.bed \
              -o /output/
done
```

## Performance Tips

1. **Pre-pull the image**: `docker pull sahuno/igver:latest`
2. **Use specific version tags**: `sahuno/igver:2.19.5` for reproducibility
3. **Mount only necessary directories** to reduce overhead
4. **Process multiple regions in one command** rather than multiple runs

## Support

For issues specific to Docker usage:
- Check this guide first
- Use `--debug` flag for detailed error messages
- Report issues at: https://github.com/sahuno/igver/issues