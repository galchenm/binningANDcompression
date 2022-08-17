#!/usr/bin/env python3
# coding: utf8


import os
import sys
import subprocess
import re
import glob
import concurrent.futures
import logging
import shutil

def setup_logger():
   level = logging.INFO
   logger = logging.getLogger("app")
   logger.setLevel(level)
   log_file = 'file.log'
   formatter = logging.Formatter('%(levelname)s - %(message)s')
   ch = logging.FileHandler(log_file)
   
   ch.setLevel(level)
   ch.setFormatter(formatter)
   logger.addHandler(ch)
   logger.info("Setup logger in PID {}".format(os.getpid()))

def rm_files_and_empty_dirs(root):
    logger = logging.getLogger('app')
    
    data_files=glob.glob(os.path.join(root,'*_data*.h5'))
    if len(data_files) > 0: 
        for file in data_files:
            try:
                data_dim = subprocess.check_output(['/opt/hdf5/hdf5-1.10.5/bin/h5ls', file +'/entry/data'])
                data_dim = data_dim.strip().decode('utf-8').split('Dataset ')[1]
                num = int(re.sub(r'({|})','',data_dim).split('/')[0])
                if num == 0:
                    
                    logger.info('The file {} is empty.\n'.format(os.path.basename(file)))
                    os.remove(file)
            except subprocess.CalledProcessError as e:
                logger.info('Impossible to open file {}.\n'.format(os.path.basename(file)))
                
    
    if len(glob.glob(os.path.join(root,'*_data*.h5'))) == 0:
        logger.info('The folder {} is empty.\n'.format(root))
        shutil.rmtree(root, ignore_errors=True)
    
    return f'Finished work with {root}'


def main():
    input_path = sys.argv[1]
    folders = [x[0] for x in os.walk(input_path) if x[0] != input_path]
    

    logger = logging.getLogger('app')
    logger.info("main")


    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = [ executor.submit(rm_files_and_empty_dirs, folder) for folder in folders]
        
        for f in concurrent.futures.as_completed(results):
            print(f.result())

setup_logger()

if __name__ == "__main__":
    main()
