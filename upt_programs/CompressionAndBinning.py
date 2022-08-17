#!/usr/bin/env python3
# coding: utf8

"""
run=$1
inputdir=$2
outdir=$3
python3 CompressionAndBinning.py -f [name of file with list of blocks] -i [input dir with raw file] -o [output dir where to save result]
"""


import os
import sys

import re
import argparse
from collections import defaultdict
import numpy as np

from multiprocessing import Pool, TimeoutError


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-f', type=str, help='File with blocks')
    parser.add_argument('-i', type=str, help="Input dir with raw file")
    parser.add_argument('-o', type=str, help="Output dir where to save result")
    return parser.parse_args()

def prepare_blocks(blocks):
    d = defaultdict(dict)
    file = open(blocks, 'r')
    for line in file:
        key,template=line.strip().split(':')
        d[key]['template'] = template
        
        blocks = re.findall(r"[\w]+[_\d]*", key) #re.findall(r"\d+[_\d]*", key)
        delimeter = re.findall(r"[-,]", key)
        if ',' in delimeter or len(blocks) == 1:
            d[key]['blocks'] = blocks
        else: #delimeter is '-'
            if len(blocks) > 2:
                print("WARNING: separate this line {} accroding to the rule of block file.\n".format(key))
            else:
                f,l = blocks
                print(f,l)
                if re.search(r"_",f) and re.search(r"_", l):
                    f_suf = re.sub(r"_",'', re.findall(r"_\d+",f)[0])
                    f_pref = re.sub(r"_",'', re.findall(r"\w+_",f)[0])
                    l_suf = re.sub(r"_",'', re.findall(r"_\d+",l)[0])
                    l_pref = re.sub(r"_",'', re.findall(r"\w+_",l)[0])

                    if f_pref != l_pref:
                        print("WARNING: this line {} could not be processed, because they have various prefix. Split these blocks into blocks with the same prefix!\n".format(key))
                        d[key]['blocks'] = []
                    else:
                        r = np.arange(int(f_suf), int(l_suf) + 1)
                        rr = [f_pref+"_"+str(i) for i in r]
                        d[key]['blocks'] = rr
                elif re.search(r"_",f) and not re.search(r"_", l) or not re.search(r"_",f) and re.search(r"_", l):
                    print("WARNING: this line {} could not be processed because parts have different type of name! Split them.\n".format(key))
                else:
                    if len(str(int(f)))!= len(str(int(l))) and len(f) == len(l):
                        pref = os.path.commonprefix([f,l])
                        d[key]['blocks'] = [pref + str(i) if len(pref + str(i)) == len(f) else pref + pref[0 : len(f) - len(pref + str(i))] + str(i) for i in np.arange(int(f), int(l) + 1)]
                    else:
                        pref = os.path.commonprefix([f,l])
                        
                        if len(pref)>0:
                            ff = f.replace(pref,'',1)
                            ll = l.replace(pref,'',1)
                            
                            d[key]['blocks'] = [pref+str(i) for i in np.arange(int(ff), int(ll) + 1)]
                        else:
                            d[key]['blocks'] = [str(i) for i in np.arange(int(f), int(l) + 1)]
    
    return d

'''
def run_compression(run):
    global blocks_dict
    global input_dir
    global output_dir
    command = 'source /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/run_binning_compression.sh {} {} {} {}'.format(run, input_dir, output_dir, template)
    os.system(command)
'''

def tolstikova_function(name_of_blocks):
    
    '''
    run=$1
    inputdir=$2
    outdir=$3
    template=$4
    '''
    
    global blocks_dict
    global input_dir
    global output_dir
    
    
    template = blocks_dict[name_of_blocks]['template']
    runs = blocks_dict[name_of_blocks]['blocks']
    
    for run in runs:
        command = 'source /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/run_binning_compression.sh {} {} {} {}'.format(run, input_dir, output_dir, template)
        os.system(command)
  
if __name__ == "__main__":
    args = parse_cmdline_args()
    
    blocks = args.f
    input_dir = args.i
    output_dir = args.o

    blocks_dict = prepare_blocks(blocks)
    name_of_blocks = blocks_dict.keys()

    print(blocks_dict)

    with Pool(processes=10) as pool:
        pool.map(tolstikova_function, name_of_blocks)