# IGVer
Conveniently take IGV snapshots in multiple bam files over mutliple regions.

## Prerequisites
- The standard way of running `igver.py` is through docker or singularity. 
- Supports genomes listed in the [genomes.json](https://s3.amazonaws.com/igv.org.genomes/genomes.json) from the IGV team.

## Installation
```bash
pip install igver
```
I would also suggest you pull the IGVer singularity container so it's saved to your cache, as follows. This is to ensure you're using an environment where the following are present. Also, since `igver` functions will invoke `singularity` anyways, pulling the image allows you to use the cached image instead of having to pull the image on the fly.
- `xvfb-run` (required to redirect IGV GUI to an image)
- IGV jar files, and
- IGV genome dictionaries (as in [IGV Hosted Genome List](https://github.com/igvteam/igv/wiki/Downloading-Hosted-Genomes-for-Offline-Use/26e9731ef36889a974b0b6fa94fce7b36d67543e#hosted-genome-list)
```
singularity pull docker://quay.io/soymintc/igver
```

## Features
- Load BAM files and visualize genomic regions using IGV
- Generate IGV batch scripts programmatically
- Run IGV inside a Singularity container for reproducibility
- Save IGV screenshots as high-resolution PNG files
- Load screenshots directly into Matplotlib figures for visualization

## Usage

### CLI

#### Example

```
igver \
  -i test/test_tumor.bam test/test_normal.bam \
  -r 8:32534767-32536767 "19:16780041-16782041 19:17553189-17555189" \
  -o ./
```

Creates two png files:

1. `./8-32534767-32536767.png` for one IGV region panel
![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.png)

2. `./19-16780041-16782041.19-17553189-17555189.png` for two IGV region panels
![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-16780041-16782041.19-17553189-17555189.png)


#### API

- `igver --help` gives:
```bash
usage: igver [-h] -i INPUT [INPUT ...] -r REGIONS [REGIONS ...] [-o OUTPUT] [-g GENOME] [--dpi DPI] 
             [--igv-dir IGV_DIR] [-p MAX_PANEL_HEIGHT] [-d {expand,collapse,squish}] [-c IGV_CONFIG]
             [--singularity-image SINGULARITY_IMAGE] [--singularity-args SINGULARITY_ARGS] [--debug]

IGVer: A tool for generating IGV screenshots

options:
  -h, --help            show this help message and exit
  -i INPUT [INPUT ...], --input INPUT [INPUT ...]
                        Input BAM, BEDPE, VCF, or bigWig file(s)
  -r REGIONS [REGIONS ...], --regions REGIONS [REGIONS ...]
                        Genomic regions (e.g., chr1:100000-200000) or regions file (e.g. regions.txt)
  -o OUTPUT, --output OUTPUT
                        Output directory for screenshots (default: /tmp)
  -g GENOME, --genome GENOME
                        Genome reference (default: hg19)
  --dpi DPI             DPI for output images (default: 300)
  --igv-dir IGV_DIR     Path to IGV installation (default: /opt/IGV_2.14.1)
  -p MAX_PANEL_HEIGHT, --max-panel-height MAX_PANEL_HEIGHT
                        Maximum panel height for IGV (default: 200).
  -d {expand,collapse,squish}, --overlap-display {expand,collapse,squish}
                        Display mode for overlapping reads (default: squish).
  -c IGV_CONFIG, --igv-config IGV_CONFIG
                        Path to additional IGV preferences file (optional).
  --singularity-image SINGULARITY_IMAGE
                        `singularity` image path (default: docker://quay.io/soymintc/igver)
  --singularity-args SINGULARITY_ARGS
                        `singularity` arguments string (default: "-B /home")
  --debug               Enable debug logging
```

### Python

#### Example

```python
import igver

bam_paths = ['./test/test_tumor.bam', './test/test_normal.bam']
regions = [
    "8:32534767-32536767",
    "19:16780041-16782041 19:17553189-17555189",
]
figures = igver.load_screenshots(bam_paths, regions)
```

Returns two figures:

1. `figures[0]` for region `8:32534767-32536767`
![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.png)

2. `figures[1]` for region `19:16780041-16782041 19:17553189-17555189`
![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-16780041-16782041.19-17553189-17555189.png)

Which you can also use `.savefig` to save into a given path.

#### API

```python
import igver
help(igver.load_screenshots)
```
Will give you
```
load_screenshot(paths, regions, output_dir='/tmp', genome='hg19', igv_dir='/opt/IGV_2.14.1', overwrite=True, remove_png=True, dpi=300, singularity_image='docker://quay.io/soymintc/igver', singularity_args='-B /home', debug=False, **kwargs)
    Generates IGV screenshots and loads them into a Matplotlib figure.
    
    Parameters:
        paths (list of str): Paths to input files (BAM, BEDPE, VCF, bigWig, etc).
        regions (list of str): List of genomic regions in 'chr:start-end' format.
        output_dir (str, optional): Directory for output screenshots (default: "/tmp").
        genome (str, optional): Genome version (default: "hg19").
        igv_dir (str, optional): Directory containing IGV installation (default: "/opt/IGV_2.14.1").
        overwrite (bool, optional): Whether to overwrite existing PNG files (default: True).
        remove_png (bool, optional): Whether to remove created PNG files (default: True).
        dpi (int, optional): DPI of the figure (default: 300).
        singularity_image (str, optional): singularity image path (default: "docker://quay.io/soymintc/igver").
        singularity_args (str, optional): singularity arguments string (default: "-B /home").
        debug (bool, optional): Whether to show logs for debugging (default: False).
        **kwargs (optional): *kwargs* such as tag, max_panel_height, overlap_display, igv_config for create_batch_script
    
    Returns:
        matplotlib.figure.Figure: Matplotlib figure containing the IGV screenshots.
```


### Additional IGV Preferences
- You can plug in additional IGV preferences as in https://github.com/igvteam/igv/wiki/Batch-commands -- an example would be `test/tag_haplotype.batch`:
```
group TAG HP
colorBy TAG rl
sort READNAME
```

### Caveat: Setting IGV Screenshot Width
- AFAIK, the only way to modify the batch screenshot width is by modifying your `${IGV_DIR}/prefs.properties` file. There is a line that looks something like `IGV.Bounds=0,0,640,480`, meaning that IGV set the bounds of the left, top, width, height (refer to https://github.com/igvteam/igv/issues/161). I've tried to override this but seems that it doesn't work that way. For the example below, I've fixed my prefs.properties file so that the screenshot width is 800 (i.e. set `IGV.Bounds=0,0,800,480`).

## Detailed CLI Usage Example
- An example command getting two bam files as inputr, displayed vertically in the order put in (i.e. top panel: `haplotag_tumor.bam`, bottom panel: `haplotag_normal.bam`), is as follows.
- Here, `test/tag_haplotype.batch` includes additional IGV preferences to group and color haplotagged reads, as written above.
```bash
igver \
    -i test/test_tumor.bam test/test_normal.bam \
    -r test/regions.txt \
    -o test/snapshots \
    -p 500 -d squish \
    -c test/tag_haplotype.batch
```
- The regions file for the test case, `test/regions.txt`, includes 4 lines of different regions. The number of regions in the same line will lead to a snapshot with the regions horizontally aligned. You can annotate the region with an optional final field, which you can omit.
- Here's the content of `test/regions.txt` and some explanation below.
```
8:32534767-32536767 region_of_interest
8:32534767-32536767 19:11137898-11139898 translocation
19:16780041-16782041 19:17553189-17555189 inversion
19:12874447-12876447 19:13500000-13501000 19:14461465-14463465 duplication
```
1. The first region will take a 1001bp;1001bp snapshot on the region coined "region of interest", and create a png file `8-32534767-32536767.region_of_interest.png` in the OUTDIR.
2. The second region will take a 1001bp;1001bp snapshot on the two breakpoints of the translocation, and create a png file `8-32534767-32536767.19-11137898-11139898.translocation.png` in the OUTDIR.
3. The third region will take a 1001bp;1001bp snapshot on the two breakpoints of the inversion, and create a png file `19-16780041-16782041.19-17553189-17555189.inversion.png` in the OUTDIR.
4. The fourth region will take a 1001bp;1001bp;1001bp snapshot on the two breakpoints and a region inbetween, and create a png file `19-12874447-12876447.19-13500000-13501000.19-14461465-14463465.duplication.png` in the OUTDIR.
- You can see that the png files in OUTDIR includes `.tumor` as a suffix. This is because the default TAG of the `--tag / -t` option is "tumor". You can set it to "None" to omit tagging the suffix.

## Example results
- You can see the IGV snapshots already taken using the script above in `test/snapshots`.

1. **Region of interest**

![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.region_of_interest.png)

2. **Translocation**

![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/8-32534767-32536767.19-11137898-11139898.translocation.png)

3. **Inversion**

![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-16780041-16782041.19-17553189-17555189.inversion.png)

4. **Duplication**

![](https://github.com/shahcompbio/igver/blob/main/test/snapshots/19-12874447-12876447.19-13500000-13501000.19-14461465-14463465.duplication.png)


