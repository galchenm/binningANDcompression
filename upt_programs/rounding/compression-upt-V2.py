import glob
import os
import sys

from multiprocessing import Pool, TimeoutError
import argparse

'''
python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compression.py [--p [path], --f [file]] -h5p [h5path to initial data] -h5pTo [path to compressed data] --[flag for compression] [-n power for non-equidistant compression or the step for equidistant compression]

'''

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-o','--o', type=str, help="Output path")    
    parser.add_argument('-s','--s', type=str, help="Single HDF5 file that you want to have a convertion")
    parser.add_argument('-p','--p', type=str, help="The path of folder/s that contain/s HDF5 files")
    parser.add_argument('-f','--f', type=str, help="The file contains HDF5 files of interest")
    parser.add_argument('-h5p', type=str, help="h5path to data in .h5/cxi files")
    parser.add_argument('-h5pTo', type=str, help="h5path where to data in .h5/cxi files")
    parser.add_argument("--eq", default=False, action="store" , help="Use this flag if you want to have a compression with equidistant layer")
    parser.add_argument("--hv", default=False, action="store" , help="Use this flag if you want to have a photon compression with equidistant layer")
    parser.add_argument("--neqWo", default=False, action="store" , help="Use this flag if you want a compression with non-equidistant layer")
    parser.add_argument("--neqWith", default=False, action="store" , help="Use this flag if you want a compression with non-equidistant sublayers")
    parser.add_argument('-n','--n',type=int, help="Treshold for values for a compression with equidistant layer or power for a compression with non-equidistant layer or number of bits for rounding to N bits")
    parser.add_argument('-lim_up', '--lim_up', type=int, help="Treshold for values or power if you use sqrt" )
    parser.add_argument('-c','--c', default=False, action="store", help="Use this flag if you want to compress data")
    parser.add_argument('-d','--d', default=False, action="store", help="Use this flag if you want to decompress data")
    parser.add_argument('-r','--r', default=False, action="store", help="Use this flag if you want to round data to N bits")
    return parser.parse_args()

def to_round_Nbits(file, outputpath, N, lim_up):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/rounding_Nbits.py {file} {path_to_data_cxi} {path_to_data} {outputpath} {N} {lim_up}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)

def to_compress(file, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/compressor.py {file} {path_to_data_cxi} {path_to_data} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)
    
    
def to_decompress(file, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/decompressor.py {file} {path_to_data_cxi} {path_to_data} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)    

def int_compression_function_eq(file, N, lim_up, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/int_compression-upt.py {file} {path_to_data_cxi} {path_to_data} {N} {lim_up} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def photon_compression_function_eq(file, N, lim_up, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/photon_compression.py {file} {path_to_data_cxi} {path_to_data} {N} {lim_up} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def noneq_wo_layer_compression_upt_function(file, N, lim_up, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/noneq_wo_layer_compression_upt.py {file} {path_to_data_cxi} {path_to_data} {N} {lim_up} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)


def noneq_with_layer_compression_upt_function(file, N, lim_up, outputpath):
    job_file = file.split('.')[0] + '.sh'
    with open(job_file, 'w+') as fh:
        fh.writelines("#!/bin/sh\n")
        fh.writelines("#SBATCH --job=%s.job\n" % os.path.basename(file).split('.')[0])
        fh.writelines("#SBATCH --partition=upex\n")
        fh.writelines("#SBATCH --time=280:00:00\n")
        fh.writelines("#SBATCH --nodes=1\n")
        fh.writelines("#SBATCH --mem=500000\n")
        fh.writelines("module load anaconda3/5.2\n")
        command = f'python3 /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/rounding/noneq_with_layer_compression_upt.py {file} {path_to_data_cxi} {path_to_data} {N} {lim_up} {outputpath}'
        #print(command)
        fh.writelines(command)
    os.system("sbatch %s" % job_file)



if __name__ == "__main__":
    global path_to_data_cxi
    global path_to_data
    args = parse_cmdline_args()
    path_to_data_cxi = args.h5p
    path_to_data = args.h5pTo
    outputpath = args.o
    if outputpath is not None and not os.path.exists(outputpath):
        os.mkdir(outputpath)
        
    lim_up = args.lim_up
    
    
    if args.p is not None:
        path_from = args.p
        
        files = glob.glob(os.path.join(path_from, '*.cxi'))
        if len(files) == 0:
            files = glob.glob(os.path.join(path_from, '*data*.h5'))
        if len(files) == 0:
            files = glob.glob(os.path.join(path_from, '*.h5'))
        if len(files) > 0:
            if args.eq:
                for file in files:
                    int_compression_function_eq(file, args.n, lim_up, outputpath)
            if args.hv:
                for file in files:
                    photon_compression_function_eq(file, args.n, lim_up, outputpath)                                
            if args.neqWo:
                for file in files:
                    noneq_wo_layer_compression_upt_function(file, args.n, lim_up, outputpath)
            if args.neqWith:
                for file in files:
                    noneq_with_layer_compression_upt_function(file, args.n, lim_up, outputpath)
            if args.c:
                print('Here')
                for file in files:
                    to_compress(file, outputpath)     
            if args.d:
                for file in files:
                    to_decompress(file, outputpath) 
            if args.r:
                for file in files:
                    to_round_Nbits(file, outputpath, args.n, lim_up)  
        else:
            for path, dirs, all_files in os.walk(path_from):
                for cdir in dirs:
                    path_from_dir = os.path.join(path, cdir)
                    if 'S000' not in cdir:
                        files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
                        if len(files) == 0:
                            files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
                        if len(files) == 0:
                            files = glob.glob(os.path.join(path_from_dir, '*.h5'))
                        if len(files) > 0:
                            if args.eq:
                                for file in files:
                                    int_compression_function_eq(file, args.n, lim_up, outputpath)
                            if args.hv:
                                for file in files:
                                    photon_compression_function_eq(file, args.n, lim_up, outputpath)                                
                            if args.neqWo:
                                for file in files:
                                    noneq_wo_layer_compression_upt_function(file, args.n, lim_up, outputpath)
                            if args.neqWith:
                                for file in files:
                                    noneq_with_layer_compression_upt_function(file, args.n, lim_up, outputpath)
                            if args.c:
                                for file in files:
                                    to_compress(file, outputpath)     
                            if args.d:
                                for file in files:
                                    to_decompress(file, outputpath) 
                            if args.r:
                                for file in files:
                                    to_round_Nbits(file, outputpath, args.n, lim_up)                                 
    elif args.f is not None:
        with open(args.f, 'r') as f:
            if args.eq:
                for file in f:
                    if len(file.strip()) != 0:
                        int_compression_function_eq(file.strip(), args.n, lim_up, outputpath)                    
            if args.hv:
                for file in f:
                    if len(file.strip()) != 0:
                        photon_compression_function_eq(file.strip(), args.n, lim_up, outputpath)               
            if args.neqWo:
                for file in f:
                    if len(file.strip()) != 0:
                        noneq_wo_layer_compression_upt_function(file.strip(), args.n, lim_up, outputpath)
            if args.neqWith:
                for file in f:
                    if len(file.strip()) != 0:
                        noneq_with_layer_compression_upt_function(file.strip(), args.n, lim_up, outputpath)
            if args.c:
                for file in f:
                    if len(file.strip()) != 0:
                        to_compress(file.strip(), outputpath)     
            if args.d:
                for file in f:
                    if len(file.strip()) != 0:
                        to_decompress(file.strip(), outputpath)  
            if args.r:
                for file in f:
                    if len(file.strip()) != 0:
                        to_round_Nbits(file.strip(), outputpath, args.n, lim_up)                        
    elif args.s is not None:
        file = args.s
        if args.eq:
            int_compression_function_eq(file, args.n, lim_up, outputpath)                    
        if args.hv:
            photon_compression_function_eq(file, args.n, lim_up, outputpath)               
        if args.neqWo:
            noneq_wo_layer_compression_upt_function(file, args.n, lim_up, outputpath)
        if args.neqWith:
            noneq_with_layer_compression_upt_function(file, args.n, lim_up, outputpath)
        if args.c:
            to_compress(file, outputpath)   
        if args.d:
            to_compress(file, outputpath)      
        if args.r:
            to_round_Nbits(file, outputpath, args.n, lim_up)            
    else:
        print("You need to provide the path or file with files for compression")    
           

