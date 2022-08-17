import os
import sys
import numpy as np
import h5py as h5
import argparse


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-s','--s', type=str, help="Single HDF5 file that you want to have a convertion")
    parser.add_argument('-p','--p', type=str, help="The path of folder/s that contain/s HDF5 files")
    parser.add_argument('-f','--f', type=str, help="The file contains HDF5 files of interest")
    parser.add_argument('-h5p', type=str, help="h5path to data in .h5/cxi files")
    parser.add_argument('-h5pTo', type=str, help="h5path where to data in .h5/cxi files")
    parser.add_argument('-c','--c', default=False, action="store" , help="Use this flag if you want to compress data")
    parser.add_argument('-d','--d', default=False, action="store" , help="Use this flag if you want to decompress data")
    parser.add_argument('-lim_up', '--lim_up', type=int, help="Treshold for values or power if you use sqrt" )
    return parser.parse_args()
 
def compressor(file, path_to_data_cxi, path_to_data):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compressor.py {file} {path_to_data_cxi} {path_to_data}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file) 

def decompressor(file, path_to_data_cxi, path_to_data):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/decompressor.py {file} {path_to_data_cxi} {path_to_data}'
        print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)  

if __name__ == "__main__":
    args = parse_cmdline_args()
    path_to_data_cxi = args.h5p
    path_to_data = args.h5pTo
    
    #lim_up = args.lim_up
    
    if args.p is not None:
        path_from = args.p
        for path, dirs, all_files in os.walk(path_from):
            
            for cdir in dirs:
                path_from_dir = os.path.join(path, cdir)
                if 'S000' not in cdir:
                    
                    files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
                    if len(files) == 0:
                        files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
                    
                    if len(files) > 0:
                        if args.c:
                            for file in files:
                                compressor(file, path_to_data_cxi, path_to_data)
                        if args.d:
                            for file in files:
                                decompressor(file, path_to_data_cxi, path_to_data)                                                 
    elif args.f is not None:
        with open(args.f, 'r') as f:
            if args.c:
                for file in f:
                    if len(file.strip()) != 0:
                        compressor(file, path_to_data_cxi, path_to_data)                    
            if args.d:
                for file in f:
                    if len(file.strip()) != 0:
                        decompressor(file, path_to_data_cxi, path_to_data)               
    elif args.s is not None:
        file = args.s
        if args.c:
            compressor(file, path_to_data_cxi, path_to_data)                    
        if args.d:
            decompressor(file, path_to_data_cxi, path_to_data)
    else:
        print("You need to provide the path or file with files for compression")    
           