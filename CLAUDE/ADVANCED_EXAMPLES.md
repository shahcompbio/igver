# Advanced IGVer Examples

This document contains detailed examples and use cases for IGVer.

## Structural Variant Visualization

IGVer is particularly useful for visualizing structural variants across multiple samples.

### Example regions.txt Format
```
8:32534767-32536767 region_of_interest
8:32534767-32536767 19:11137898-11139898 translocation
19:16780041-16782041 19:17553189-17555189 inversion
19:12874447-12876447 19:13500000-13501000 19:14461465-14463465 duplication
```

This file format allows you to:
1. Single region with annotation
2. Two regions (breakpoints) for translocations
3. Two regions for inversions
4. Three or more regions for complex events

### Detailed Command Example
```bash
igver \
    -i test/haplotag_tumor.bam test/haplotag_normal.bam \
    -r test/regions.txt \
    -o test/snapshots \
    -p 500 -d squish \
    -c test/tag_haplotype.batch
```

### Output Files
Based on the regions.txt above, this will create:
1. `8-32534767-32536767.region_of_interest.png`
2. `8-32534767-32536767.19-11137898-11139898.translocation.png`
3. `19-16780041-16782041.19-17553189-17555189.inversion.png`
4. `19-12874447-12876447.19-13500000-13501000.19-14461465-14463465.duplication.png`

## Custom IGV Preferences

### Haplotype Visualization
For phased/haplotagged reads:
```
# tag_haplotype.batch
group TAG HP
colorBy TAG HP
sort READNAME
```

### Read Group Coloring
```
# read_groups.batch
group TAG RG
colorBy TAG RG
sort BASE
```

### Coverage Track Settings
```
# coverage.batch
setDataRange 0 100
colorBy UNEXPECTED_PAIR
viewaspairs
```

## Batch Processing Scripts

### Process Multiple Samples
```bash
#!/bin/bash
# process_samples.sh

SAMPLES="sample1 sample2 sample3"
REGIONS="regions.bed"

for sample in $SAMPLES; do
    echo "Processing $sample..."
    igver \
        -i ${sample}.bam \
        -r $REGIONS \
        -o screenshots/${sample} \
        --singularity-image docker://sahuno/igver:latest
done
```

### Parallel Processing with GNU Parallel
```bash
# Create sample list
ls *.bam > samples.txt

# Run in parallel (4 jobs at a time)
cat samples.txt | parallel -j 4 'igver -i {} -r regions.bed -o screenshots/{/.}'
```

## HPC Submission Scripts

### SLURM Example
```bash
#!/bin/bash
#SBATCH --job-name=igver_batch
#SBATCH --time=2:00:00
#SBATCH --mem=16G
#SBATCH --cpus-per-task=4
#SBATCH --array=1-100

module load singularity

# Get sample from array
SAMPLE=$(sed -n "${SLURM_ARRAY_TASK_ID}p" sample_list.txt)

# Run IGVer
singularity exec --bind /data,/scratch \
    docker://sahuno/igver:latest \
    igver.py \
    -i /data/bams/${SAMPLE}.bam \
    -r /data/regions/regions.bed \
    -o /scratch/screenshots/${SAMPLE}
```

### SGE/UGE Example
```bash
#!/bin/bash
#$ -N igver_screenshots
#$ -t 1-100
#$ -l h_vmem=16G
#$ -pe smp 1

SAMPLE=$(sed -n "${SGE_TASK_ID}p" sample_list.txt)

singularity exec --bind /data \
    docker://sahuno/igver:latest \
    igver.py \
    -i /data/${SAMPLE}.bam \
    -r regions.bed \
    -o screenshots/${SAMPLE}
```

## Working with Different Genome Builds

### Human Genomes
```bash
# GRCh37/hg19
igver -i sample.bam -r regions.bed -g hg19 -o output/

# GRCh38/hg38
igver -i sample.bam -r regions.bed -g hg38 -o output/

# T2T-CHM13 (if added to container)
igver -i sample.bam -r regions.bed -g hs1 -o output/
```

### Model Organisms
```bash
# Mouse mm10
igver -i mouse_sample.bam -r mouse_regions.bed -g mm10 -o output/

# Mouse mm39
igver -i mouse_sample.bam -r mouse_regions.bed -g mm39 -o output/

# Zebrafish
igver -i zebrafish.bam -r zf_regions.bed -g danRer11 -o output/
```

## Example Gallery

### Region of Interest
![Region of Interest](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.region_of_interest.png)

### Translocation
![Translocation](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.19-11137898-11139898.translocation.png)

### Inversion
![Inversion](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-16780041-16782041.19-17553189-17555189.inversion.png)

### Duplication
![Duplication](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-12874447-12876447.19-13500000-13501000.19-14461465-14463465.duplication.png)

## Tips and Tricks

### Adjusting Screenshot Width
To modify the screenshot width, you need to edit the IGV preferences:
```bash
# Inside the container
echo "IGV.Bounds=0,0,1200,600" >> /opt/IGV_2.19.5/prefs.properties
```

### Creating Custom Containers
If you need custom genomes or settings:
```dockerfile
FROM sahuno/igver:latest

# Add custom genome
ADD my_genome.json /opt/IGV_2.19.5/genomes/

# Add custom preferences
ADD prefs.properties /opt/IGV_2.19.5/
```

### Memory Optimization
For large BAM files or many regions:
```bash
# Increase Java heap size
export IGV_JAVA_OPTIONS="-Xmx8g"
igver -i large.bam -r many_regions.bed -o output/
```