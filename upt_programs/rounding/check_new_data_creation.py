import glob
import os
import sys
import h5py as h5
from multiprocessing import Pool, TimeoutError
import argparse

'''

'''

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-p','--p', type=str, help="The path of folder/s that contain/s HDF5 files")
    parser.add_argument('-f','--f', type=str, help="The file contains HDF5 files of interest")
    parser.add_argument('-h5p', type=str, help="h5path to data in .h5/cxi files")
    parser.add_argument('-h5pTo', type=str, help="h5path where to data in .h5/cxi files")
    return parser.parse_args()

def check(file_cxi, path_to_data_cxi, path_to_data):
    global success
    files_wo_link = open('notprocessed.lst', 'a')
    f = h5.File(file_cxi, 'r')
    data_initial = f[path_to_data_cxi]
    
    if path_to_data in f:
        data_final = f[path_to_data]
        shape_data_initial = data_initial.shape
        shape_data_final = data_final.shape
        if shape_data_initial != shape_data_final:
            print(f"ErrorNotFinishedWriting: {os.path.basename(file_cxi)}\n")
            success = False
    else:
        print(f"ErrorNoLinkToData: {os.path.basename(file_cxi)}\n")
        files_wo_link.write(file_cxi+"\n")
    f.close()
    files_wo_link.close()



if __name__ == "__main__":
    args = parse_cmdline_args()
    path_from = args.p
    path_to_data_cxi = args.h5p
    path_to_data = args.h5pTo
    
    success = True
    if path_from is not None:
        if len(glob.glob(os.path.join(path_from, '*.cxi'))) != 0 or len(glob.glob(os.path.join(path_from, '*data*.h5'))) != 0:
            files = glob.glob(os.path.join(path_from, '*.cxi')) if len(glob.glob(os.path.join(path_from, '*.cxi'))) != 0 else glob.glob(os.path.join(path_from, '*data*.h5'))
            for file_cxi in files:
                check(file_cxi, path_to_data_cxi, path_to_data)
        else:
            for path, dirs, all_files in os.walk(path_from):
                for cdir in dirs:
                    path_from_dir = os.path.join(path, cdir)
                    if 'S000' not in cdir:
                        
                        files = glob.glob(os.path.join(path_from_dir, '*.cxi'))
                        if len(files) == 0:
                            files = glob.glob(os.path.join(path_from_dir, '*data*.h5'))
                        
                        if len(files) > 0:
                            for file_cxi in files:
                                check(file_cxi, path_to_data_cxi, path_to_data)
                        else:
                            print(f'{path_from_dir} does not contain any HDF5 files')
                if success:
                    print('All is compressed')
                    os.remove('notprocessed.lst')
                else:
                    print(f"Check notprocessed.lst")
    elif args.f is not None:
        with open(args.f, 'r') as f:
            for file_cxi in f:
                if len(file_cxi.strip()) != 0:
                    check(file_cxi.strip(), path_to_data_cxi, path_to_data)
        if success:
            print('All is compressed')
            os.remove('notprocessed.lst')
        else:
            print(f"Check notprocessed.lst")                

    else:
        print("You need to provide the path or file with files")                  
            

