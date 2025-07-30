#!/usr/bin/env python3

import argparse
import os
import sys
import yaml

# Add package root to sys.path when running as a script
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from igver import load_screenshots

try:
    from importlib import resources  # Python 3.9+
except ImportError:
    import importlib_resources as resources  # Backport for Python 3.7-3.8


def parse_args():
    parser = argparse.ArgumentParser(
        description="IGVer: A tool for generating IGV screenshots"
    )
    parser.add_argument(
        "-i", "--input", nargs="+", required=True, help="Input BAM, BEDPE, VCF, or bigWig file(s)"
    )
    parser.add_argument(
        "-r", "--regions", nargs="+", required=True, help='Genomic regions (e.g., chr1:100000-200000) or regions file (e.g. region.txt or regions.bed)'
    )
    parser.add_argument(
        "-o", "--output", default="/tmp", help="Output directory for screenshots (default: /tmp)"
    )
    parser.add_argument(
        "-g", "--genome", default="hg19", help="Genome reference (default: hg19)"
    )
    parser.add_argument(
        "--dpi", type=int, default=300, help="DPI for output images (default: 300)"
    )
    parser.add_argument(
        "--igv-dir",
        default="/opt/IGV_2.19.5", 
        help="Path to IGV installation (default: /opt/IGV_2.19.5)"
    )
    parser.add_argument(
        "-p", "--max-panel-height",
        type=int,
        default=200,
        help="Maximum panel height for IGV (default: 200)."
    )
    parser.add_argument(
        "-d", "--overlap-display",
        choices=["expand", "collapse", "squish"],
        default="squish",
        help="Display mode for overlapping reads (default: squish)."
    )
    parser.add_argument(
        "-c", "--igv-config",
        help="Path to additional IGV preferences file (optional)."
    )
    parser.add_argument(
        "--singularity-image", 
        default="docker://sahuno/igver:latest", 
        help="`singularity` image path (default: docker://sahuno/igver:latest)"
    )
    parser.add_argument(
        "--singularity-args", 
        default="-B /home", 
        help='`singularity` arguments string (default: "-B /home")'
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "--no-singularity", 
        action="store_true", 
        help="Run IGV directly without Singularity wrapper (auto-detected in containers)"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Output image format (default: png). Note: pdf requires svg conversion."
    )
    args = parser.parse_args()
    return args


def _load_genome_mappings():
    """Loads genome mappings from genome.yaml"""
    try:
        yaml_path = resources.files("igver.data").joinpath("genome_map.yaml")
        with yaml_path.open('r') as f:
            genome_data = yaml.safe_load(f)
        return genome_data.get("aliases", {})
    except Exception as e:
        print(f"[ERROR] Failed to load genome.yaml: {e}")
        return {}


def main():
    os.environ["DISPLAY"] = ""
    args = parse_args()

    # Ensure paths exist
    os.makedirs(args.output, exist_ok=True)
    for path in args.input:
        assert os.path.exists(path), f'[ERROR] {path} does not exist.'

    genome_map = _load_genome_mappings()
    genome = genome_map.get(args.genome, args.genome) # convert e.g. GRCh38 -> hg38

    try:
        kwargs = {
            "paths": args.input,
            "regions": args.regions,
            "output_dir": args.output,
            "genome": genome,
            "max_panel_height": args.max_panel_height,
            "overlap_display": args.overlap_display,
            "igv_dir": args.igv_dir,
            "dpi": args.dpi,
            "remove_png": False,  # don't remove output images
            "debug": args.debug,
            "output_format": args.format,
            "use_singularity": not args.no_singularity,
            "singularity_image": args.singularity_image,
            "singularity_args": args.singularity_args,
        }

        # Conditionally add `igv_config` if it's provided
        if args.igv_config:
            kwargs["igv_config"] = args.igv_config

        # Call the function with unpacked arguments
        _ = load_screenshots(**kwargs)

        print(f"[SUCCESS] Screenshots saved in: {args.output}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
