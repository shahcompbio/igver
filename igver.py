#!/usr/bin/env python

import os
import sys
import time
import uuid
import argparse
import subprocess as sp

def parse_args():
    description = 'Create temporary batchfile and run IGV for a region list'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--bam', nargs='+', help="Input tumor bam file(s) to be shown vertically", required=True)
    p.add_argument('-r', '--regions', help="Either a 'chr:start-end' string, or input regions file with region columns to be shown horizontally", required=True)
    p.add_argument('-o', '--outdir', help="Output png directory", required=True)
    p.add_argument('-g', '--genome', help="Genome version [default: 'GRCh37']", default='GRCh37')
    p.add_argument('-t', '--tag', help="Tag to suffix your png file [default: 'tumor']", default='tumor')
    p.add_argument('-mph', '--max_panel_height', help="Max panel height [default: 200]", type=int, default=200)
    p.add_argument('-od', '--overlap_display', help="'expand', 'collapse' or 'squish'; [default: 'squish']", default='squish')
    p.add_argument('--overwrite', help="Overwrite existing png files [default: False]", action="store_true")
    p.add_argument('-d', '--igv_dir', help="/path/to/IGV_x.xx.x", type=str, default="/opt/IGV_2.14.1")
    p.add_argument('--config', help="Additional preferences [default: None]", default=None)

    return p.parse_args()

def parse_multiregion_from_regfile_line(line):
    """Parse region and tag from regions file line
    """
    out_tag = ''
    sv_tag = ''
    field = line.strip().split() # split by either ' ' or '\t'
    regions = []
    region_tags = []
    for item in field:
        is_region = (item.count(':')==1 and item.count('-')==1)
        if is_region:
            region_tag = item.replace(':', '-')
            region_tags.append(region_tag)
            regions.append(item)
        else:
            sv_tag = item
    out_tag = '.'.join(region_tags)
    regions = ' '.join(regions)
    if sv_tag: out_tag += f'.{sv_tag}' # e.g. ins, del, translocation, ...
    return regions, out_tag

def make_png_filename(out_tag, args_tag=None):
    """Return png filename from out_tag
    """
    if args_tag != "None":
        out_tag += f'.{args.tag}' # e.g. tumor, normal
    png_fname = f'{out_tag}.png'
    return png_fname

def get_additional_preferences(config):
    """Return IGV preferences to insert from given config
    """
    if config:
        assert os.path.exists(config), f'[ERROR:{time.ctime()}] Additional preferences file {config} does not exist'
        additional_pref = open(config, 'r').read().rstrip()
        return additional_pref + '\n'
    return None

def make_batchfile(args):
    """Create IGV batchfile for automated screenshots
    """
    # get additional preferences
    additional_pref = get_additional_preferences(args.config)
    # create batch file
    uuid_str = str(uuid.uuid4())
    tmp_batchname = f'_{uuid_str}.batch'
    png_paths = []
    with open(tmp_batchname, 'w') as batch:
        batch.write('new\n')
        batch.write(f'snapshotDirectory {args.outdir}\n')
        batch.write(f'genome {args.genome}\n') # TODO: check file
        for bam in args.bam: 
            batch.write(f'load {bam}\n')
        for line in open(args.regions, 'r'):
            # one snapshot per region[s]
            regions, out_tag = parse_multiregion_from_regfile_line(line)
            png_fname = make_png_filename(out_tag, args_tag=args.tag)
            batch.write(f'goto {regions}\n') # goto region1 region2 ...
            if args.overlap_display != 'expand':
                batch.write(f'{args.overlap_display}\n') # expand squish collapse
            #batch.write(f'preference IGV.Bounds 0,0,1280,480\n') 
            batch.write(f'maxPanelHeight {args.max_panel_height}\n') 
            if additional_pref:
                batch.write(additional_pref)
            # finally, take a snapshot
            batch.write(f'snapshot {png_fname}\n')
            png_path = os.path.join(args.outdir, png_fname)
            png_paths.append(png_path)
        batch.write('exit\n')
    return tmp_batchname, png_paths

def all_png_paths_exist(png_paths):
    """Check if all png files in input list exist
    """
    all_exists = True
    for png_path in png_paths:
        if not os.path.exists(png_path):
            all_exists = False
    return all_exists

def make_outdir_if_absent(outdir):
    """Create outdir if absent
    """
    if not os.path.exists(outdir):
        mkdir = sp.Popen(f'mkdir {outdir}', stdout=sp.PIPE, shell=True)
        mkdir_stdout = mkdir.communicate()[0].strip()
        print(f'[LOG:{time.ctime()}] mkdir {outdir}; STDOUT: {mkdir_stdout}')

def exec_igv_cmd(cmd):
    """Open subprocess for cmd, execute, print stdout
    """
    igvcmd = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
    proc_stdout = igvcmd.communicate()[0].strip()
    print(f'[LOG:{time.ctime()}] igv log:\n', proc_stdout.decode('utf-8'))

def rm_existing_files(file_paths):
    """Remove all paths in input file list
    """
    for file_path in file_paths:
        cmd = f'rm {file_path}'
        rmcmd = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        proc_stdout = rmcmd.communicate()[0].strip()
        print(f'[LOG:{time.ctime()}] {cmd}; STDOUT:', proc_stdout.decode('utf-8'))

def get_genome(genome):
    if genome == 'GRCh37' or genome == 'hg19':
        return 'hg19'
    elif genome == 'GRCh38' or genome == 'hg38':
        return 'hg38'
    else:
        return genome


def run_igv(args):
    """For bams and regions, make batchfile, run IGV, remove batchfile
    """
    assert os.path.exists(args.igv_dir), f"[ERROR:{time.ctime()}] {args.igv_dir} does not exist"
    igv_runfile = f'{args.igv_dir}/igv.sh'
    assert os.path.exists(igv_runfile), f"[ERROR:{time.ctime()}] {igv_runfile} does not exist"
    args.genome = get_genome(args.genome)

    for bam in args.bam:
        assert os.path.exists(bam), f'[ERROR:{time.ctime()}] bam: {bam} does not exist'
    display_modes = ['expand', 'collapse', 'squish']
    assert args.overlap_display in display_modes, f'[ERROR:{time.ctime()}] {args.overlap_display} not in {display_modes}'

    tmp_batchname, png_paths = make_batchfile(args)
    cmd = f'xvfb-run --auto-display --server-args="-screen 0 1920x1080x24" {igv_runfile} -b {tmp_batchname}'
    print(f'[LOG:{time.ctime()}] command:\n{cmd}')
    n_iter = 0
    while not all_png_paths_exist(png_paths):
        n_iter += 1
        print(f'[LOG:{time.ctime()}] iteration #{n_iter} to ensure all png files exist')
        exec_igv_cmd(cmd)
    if all_png_paths_exist(png_paths) and n_iter == 0:
        print(f'[LOG:{time.ctime()}] all png files already exist')
        if args.overwrite:
            rm_existing_files(png_paths)
            while not all_png_paths_exist(png_paths):
                n_iter += 1
                print(f'[LOG:{time.ctime()}] iteration #{n_iter} to ensure all png files exist')
                exec_igv_cmd(cmd)
        if n_iter == 9:
            sys.exit(f'[ERROR:{time.ctime()} 10th iteration failed -- check log. Killing job')

    rmbatch = sp.Popen(f'rm {tmp_batchname}', stdout=sp.PIPE, shell=True)
    rmbatch_stdout = rmbatch.communicate()[0].strip()
    print(f'[LOG:{time.ctime()}] rm {tmp_batchname}:\n', rmbatch_stdout.decode('utf-8'))

if __name__ == '__main__':
    args = parse_args()
    make_outdir_if_absent(args.outdir)
    run_igv(args)
