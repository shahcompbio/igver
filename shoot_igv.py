#!/usr/bin/env python

import os
import sys
import time
import uuid
import argparse
import subprocess as sp

igv_runfile = '/IGV_Linux_2.14.1/igv.sh'

def parse_args():
    description = 'Create temporary batchfile and run IGV for a region list'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--bam', nargs='+', help="Input tumor bam file(s) to be shown vertically", required=True)
    p.add_argument('-r', '--regions', help="Either a 'chr:start-end' string, or input regions file with region columns to be shown horizontally", required=True)
    p.add_argument('-o', '--outdir', help="Output png directory", required=True)
    p.add_argument('-t', '--tag', help="Tag to suffix your png file [default: 'tumor']", default='tumor')
    p.add_argument('-mph', '--max_panel_height', help="Max panel height [default: 200]", type=int, default=200)
    p.add_argument('-od', '--overlap_display', help="'expand', 'collapse' or 'squish'; [default: 'squish']", default='squish')
    p.add_argument('--overwrite', help="Overwrite existing png files [default: False]", default=False, type=bool)
    p.add_argument('--config', help="Additional preferences [default: None]", default=None)

    return p.parse_args()

def parse_multiregion_from_regfile_line(line):
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
    if args_tag:
        out_tag += f'.{args.tag}' # e.g. tumor, normal
    png_fname = f'{out_tag}.png'
    return png_fname

def get_additional_preferences(config):
    if config:
        assert os.path.exists(config), f'[ERROR:{time.ctime()}] Additional preferences file {config} does not exist'
        additional_pref = open(config, 'r').read().rstrip()
        return additional_pref + '\n'
    return None

def make_batchfile(args):
    # get additional preferences
    additional_pref = get_additional_preferences(args.config)
    # create batch file
    uuid_str = str(uuid.uuid4())
    tmp_batchname = f'_{uuid_str}.batch'
    png_paths = []
    with open(tmp_batchname, 'w') as batch:
        batch.write('new\n')
        batch.write(f'snapshotDirectory {args.outdir}\n')
        batch.write('genome hg19\n') # TODO: check file
        for bam in args.bam: 
            batch.write(f'load {bam}\n')
        for line in open(args.regions, 'r'):
            # one snapshot per region[s]
            regions, out_tag = parse_multiregion_from_regfile_line(line)
            png_fname = make_png_filename(out_tag, args_tag=args.tag)
            batch.write(f'goto {regions}\n') # goto region1 region2 ...
            if args.overlap_display != 'expand':
                batch.write(f'{args.overlap_display}\n') # expand squish collapse
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
    all_exists = True
    for png_path in png_paths:
        if not os.path.exists(png_path):
            all_exists = False
    return all_exists

def make_outdir_if_absent(outdir):
    if not os.path.exists(outdir):
        mkdir = sp.Popen(f'mkdir {outdir}', stdout=sp.PIPE, shell=True)
        mkdir_stdout = mkdir.communicate()[0].strip()
        print(f'[LOG:{time.ctime()}] mkdir {outdir}; STDOUT: {mkdir_stdout}')

def exec_igv_cmd(cmd):
    igvcmd = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
    proc_stdout = igvcmd.communicate()[0].strip()
    print(f'[LOG:{time.ctime()}] igv log:\n', proc_stdout.decode('utf-8'))

def rm_existing_pngs(png_paths):
    for png_path in png_paths:
        cmd = f'rm {png_path}'
        rmcmd = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        proc_stdout = rmcmd.communicate()[0].strip()
        print(f'[LOG:{time.ctime()}] {cmd}; STDOUT:', proc_stdout.decode('utf-8'))

def run_igv(args):
    for bam in args.bam:
        assert os.path.exists(bam), f'[ERROR:{time.ctime()}] bam: {bam} does not exist'
    display_modes = ['expand', 'collapse', 'squish']
    assert args.overlap_display in display_modes, f'[ERROR:{time.ctime()}] {args.overlap_display} not in {display_modes}'

    tmp_batchname, png_paths = make_batchfile(args)
    cmd = f'xvfb-run --auto-servernum {igv_runfile} -b {tmp_batchname}'
    print(f'[LOG:{time.ctime()}] command:\n{cmd}')
    n_iter = 0
    #while not all_png_paths_exist(png_paths):
    #    n_iter += 1
    print(f'[LOG:{time.ctime()}] iteration #{n_iter} to ensure all png files exist')
    exec_igv_cmd(cmd)
    #if all_png_paths_exist(png_paths) and n_iter == 0:
    #    print(f'[LOG:{time.ctime()}] all png files already exist')
    #    if args.overwrite:
    #        rm_existing_pngs(png_paths)
    #        while not all_png_paths_exist(png_paths):
    #            n_iter += 1
    #            print(f'[LOG:{time.ctime()}] iteration #{n_iter} to ensure all png files exist')
    #            exec_igv_cmd(cmd)

    rmbatch = sp.Popen(f'rm {tmp_batchname}', stdout=sp.PIPE, shell=True)
    rmbatch_stdout = rmbatch.communicate()[0].strip()
    print(f'[LOG:{time.ctime()}] rm {tmp_batchname}:\n', rmbatch_stdout.decode('utf-8'))

if __name__ == '__main__':
    args = parse_args()
    make_outdir_if_absent(args.outdir)
    run_igv(args)
