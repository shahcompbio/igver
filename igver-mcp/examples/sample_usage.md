# IGVer MCP Usage Examples

This document provides example usage patterns for the IGVer MCP server in Claude Code.

## Basic Usage

### Single Region Screenshot
```
Take an IGV screenshot of chr1:1000000-2000000 using /data/sample.bam
```

### Multiple Regions
```
Generate IGV screenshots for chr1:1000000-2000000 and chr2:5000000-6000000 using sample.bam
```

### Using BED Files
```
Create IGV screenshots for all regions in example_regions.bed using sample.bam with hg38 genome
```

## Advanced Usage

### Multiple Input Files
```
Compare tumor.bam and normal.bam at chr3:10000000-11000000 with high resolution
```

### Custom Output Formats
```
Generate SVG screenshots of chr1:1000000-2000000 using sample.bam for publication
```

### Batch Processing
```
Process all screenshot jobs in batch_config.yaml and save to ./batch_output/
```

## Region Validation

### Validate Single Region
```
Check if chr1:1000000-2000000 is a valid region for hg38
```

### Validate BED File
```
Validate all regions in example_regions.bed for hg19 genome
```

## Working with Different Genomes

### List Available Genomes
```
Show me all available reference genomes for IGVer
```

### Using Genome Aliases
```
Take a screenshot using GRCh38 genome (will be converted to hg38)
```

## Tips and Best Practices

1. **File Paths**: Always use absolute paths or paths relative to your current directory
2. **Genome Matching**: Ensure your BAM files match the specified genome version
3. **Output Formats**: 
   - PNG: Best for general use
   - SVG: Scalable vector graphics for publications
   - PDF: Converted from SVG, requires additional dependencies
4. **Resolution**: Default is 300 DPI, use 600+ for publication quality

## Common Workflows

### Structural Variant Visualization
```
Create split-view IGV screenshots for translocation breakpoints:
- chr8:128750000-128760000
- chr14:106330000-106340000
Using long_reads.bam with expanded view
```

### Coverage Analysis
```
Generate coverage plots for all exons in genes.bed using sample.bigWig
```

### Variant Validation
```
Take screenshots of all variants in variants.vcf +/- 500bp using sample.bam
```

## Troubleshooting Commands

### Check Container Runtime
```
What container runtime is IGVer MCP using?
```

### Debug Failed Screenshot
```
Why did the screenshot for chr1:1000000-2000000 fail?
```