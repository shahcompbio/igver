# README.md Improvement Suggestions

## 1. **Quick Start Section**
Add a "Quick Start" section right after the features for users who want to get started immediately:
```markdown
## Quick Start
```bash
# Using Singularity (recommended for HPC)
singularity exec docker://sahuno/igver:2.19.5 igver.py \
  -i sample.bam -r "chr1:1000000-2000000" -o output/

# Using local installation
pip install igver
igver -i sample.bam -r "chr1:1000000-2000000" -o output/
```

## 2. **Fix Container Image Reference**
Update the old container reference:
- Old: `docker://quay.io/soymintc/igver`
- New: `docker://sahuno/igver:2.19.5`

## 3. **Add Container Installation Section**
Replace current installation section with clearer options:
```markdown
## Installation

### Option 1: Using Container (Recommended)
```bash
# For Singularity/Apptainer
singularity pull docker://sahuno/igver:2.19.5

# For Docker
docker pull sahuno/igver:2.19.5
```

### Option 2: Local Installation
```bash
pip install igver
```
Note: Local installation requires Singularity to be installed for running IGV.
```

## 4. **Add Supported File Formats Section**
```markdown
## Supported Input Formats
- **BAM** files (requires .bai index)
- **BEDPE** files (for structural variants)
- **VCF** files
- **bigWig** files
- **BED** files for regions (BED3 and BED6)
```

## 5. **Reorganize Usage Examples**
Move the detailed examples to a more logical order:
1. Basic usage
2. BED file usage
3. Multiple regions
4. Advanced options

## 6. **Add Troubleshooting Section**
```markdown
## Troubleshooting

### Container Issues
- **Permission denied**: Add `--bind` flags for your data directories
- **Image not found**: Pull the image first with `singularity pull`

### Common Errors
- **No screenshots generated**: Check if BAM files have indexes (.bai)
- **Region not found**: Verify chromosome names match reference genome
```

## 7. **Fix Typos and Grammar**
- Line 2: "mutliple" → "multiple"
- Line 178: "inputr" → "input"

## 8. **Add Output File Naming Convention**
```markdown
## Output File Naming
- Single region: `{chr}-{start}-{end}.png`
- With BED name: `{chr}-{start}-{end}.{name}.png`
- With custom tag: `{chr}-{start}-{end}.{tag}.png`
- Multiple regions: regions separated by dots
```

## 9. **Update Python API Example**
Show how to save figures:
```python
# Save individual screenshots
for i, fig in enumerate(figures):
    fig.savefig(f'screenshot_{i}.png', dpi=300, bbox_inches='tight')
```

## 10. **Add Performance Tips**
```markdown
## Performance Tips
- Pre-pull container images to avoid download delays
- Use absolute paths for BAM files
- Ensure sufficient memory for large regions
- Use `-B` flags to bind necessary directories
```

## 11. **Add Citation/Credits**
```markdown
## Citation
If you use IGVer in your research, please cite:
[Add appropriate citation]

## License
MIT License - see LICENSE file

## Authors
- Seongmin Choi (@soymintc)
- [Other contributors]
```

## 12. **Simplify Complex Examples**
The detailed CLI example with regions.txt is too complex for main documentation. Consider moving to a separate "Advanced Usage" document or examples directory.

## 13. **Add Table of Contents**
For easier navigation:
```markdown
## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [CLI](#cli)
  - [Python API](#python)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
```

## 14. **Update Help Output**
The help output shows old version paths - needs to be regenerated with new version.

## 15. **Add Requirements Section**
```markdown
## Requirements
- Python 3.7+
- Singularity/Apptainer or Docker
- For local installation: matplotlib, Pillow
```