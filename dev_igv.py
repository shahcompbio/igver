#!/usr/bin/env python

import os
import sys
import time
import argparse
import subprocess as sp

igv_runfile = '/juno/work/shah/users/chois7/packages/IGV_Linux_2.14.1/igv.sh'

def parse_args():
    description = 'Create temporary batchfile and run IGV for a region list'
    p = argparse.ArgumentParser(description=description)
    p.add_argument('--bam', nargs='+', help="Input tumor bam file(s) to be shown vertically", required=True)
    p.add_argument('-r', '--regions', help="Either 'chr:start-end' string, or input regions file with region columns to be shown horizontally", required=True)
    p.add_argument('-o', '--outdir', help="Output png directory", required=True)
    p.add_argument('-t', '--tag', help="Tag to suffix your png file [default: 'tumor']", default='tumor')
    p.add_argument('-mph', '--max_panel_height', help="Max panel height [default: 200]", type=int, default=200)
    p.add_argument('-od', '--overlap_display', help="'expand', 'collapse' or 'squish'; [default: 'squish']", default='squish')

    return p.parse_args()

def run_igv(args):
    for bam in args.bam:
        assert os.path.exists(bam), f'[ERROR:{time.ctime()}] bam: {bam} does not exist'
    display_modes = ['expand', 'collapse', 'squish']
    assert args.overlap_display in display_modes, f'[ERROR:{time.ctime()}] {args.overlap_display} not in {display_modes}'

    for line in open(args.regions, 'r'):
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

        # Create batch file
        if sv_tag: out_tag += f'.{sv_tag}' # e.g. ins, del, translocation, ...
        if args.tag:
            out_tag += f'.{args.tag}' # e.g. tumor, normal
        tmp_batchname = f'_{out_tag}.batch'
        png_fname = f'{out_tag}.png'
        with open(tmp_batchname, 'w') as batch:
            batch.write('new\n')
            batch.write(f'snapshotDirectory {args.outdir}\n')
            for bam in args.bam: 
                batch.write(f'load {bam}\n')
            batch.write('genome hg19\n') # TODO: check file
            batch.write(f'goto {regions}\n') # goto region1 region2 ...

            # TODO: make this block input from config
            if args.overlap_display != 'expand':
                batch.write(f'{args.overlap_display}\n') # expand squish collapse
            batch.write(f'maxPanelHeight {args.max_panel_height}\n') 
            #batch.write('group TAG HP\n') # TODO: customize
            #batch.write('colorBy TAG rl\n') # TODO: customize
            #batch.write('sort READNAME\n') # TODO: customize

            batch.write(f'snapshot {png_fname}\n')
            batch.write('exit\n')

        #cmd = f'xvfb-run --auto-servernum {igv_runfile} -b {tmp_batchname}'
        cmd = f'singularity run -B /juno docker://shahcompbio/igv xvfb-run --auto-servernum {igv_runfile} -b {tmp_batchname}'
        print(f'[LOG:{time.ctime()}] command:\n{cmd}')
        process = sp.Popen(cmd, stdout=sp.PIPE, shell=True)
        proc_stdout = process.communicate()[0].strip()
        print(f'[LOG:{time.ctime()}] igv log:\n', proc_stdout.decode('utf-8'))
        rm = sp.Popen(f'rm {tmp_batchname}', stdout=sp.PIPE, shell=True)


if __name__ == '__main__':
    args = parse_args()
    if not os.path.exists(args.outdir):
        print(f'[LOG:{time.ctime()}] {args.outdir} does not exist; creating one...')
        os.mkdir(args.outdir)
    run_igv(args)
