#!/usr/bin/env python3
# coding: utf8
# Written by Galchenkova M., 2021

import os
import sys
import subprocess
from string import Template
import shlex
import re
import numpy as np
import pandas as pd
import math
from collections import defaultdict
import glob
import logging
import argparse

x_arg_name = 'd'
y_arg_name = 'CC*'

class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass

def parse_cmdline_args():
    parser = argparse.ArgumentParser(
        description=sys.modules[__name__].__doc__,
        formatter_class=CustomFormatter)
    parser.add_argument('-f', type=str, help="The file with blocks for binning")
    parser.add_argument('-i', type=str, help='Input folder with raw data')
    parser.add_argument('-p',type=str, help="The path with processed raw data")

    
    parser.add_argument('-o', type=str, help="The name of folder where you want to store results of binning")
    
    parser.add_argument('-b','--b', default=2, type=int, help="Bin size")
    parser.add_argument('-n','--n', default=3, type=int, help="Min good pix count")
    
    parser.add_argument('-maxres','--maxres',default=10**10, type=int, help="Use this flag if you want to force uce max-resolution") 
    
    parser.add_argument('-t','--t', type=str, help="Use this flag if you want to process the block of files with the same template that you add")
    parser.add_argument('--s', default=False, action='store_true', help="Use this flag if you want to skip binning in case if already processed it")
    parser.add_argument('--no-s', dest='s', action='store_false', help="Use this flag if you don not want to skip binning in case if already processed it")
    return parser.parse_args()

def setup_logger():
   level = logging.INFO
   logger = logging.getLogger("app")
   logger.setLevel(level)
   log_file = 'binning-upt2.log'
   formatter = logging.Formatter('%(levelname)s - %(message)s')
   ch = logging.FileHandler(os.path.join(os.getcwd(), log_file))
   
   ch.setLevel(level)
   ch.setFormatter(formatter)
   logger.addHandler(ch)
   logger.info("Setup logger in PID {}".format(os.getpid()))
   print("Log file is {}".format(os.path.join(os.getcwd(), log_file)))

def get_xy(file_name, x_arg_name, y_arg_name):
    x = []
    y = []

    with open(file_name, 'r') as stream:
        for line in stream:
            if y_arg_name in line:
                tmp = line.replace('1/nm', '').replace('# ', '').replace('centre', '').replace('/ A', '').replace(' dev','').replace('(A)','')
                tmp = tmp.split()
                y_index = tmp.index(y_arg_name)
                x_index = tmp.index(x_arg_name)

            else:
                tmp = line.split()
                
                x.append(float(tmp[x_index]) if not np.isnan(float(tmp[x_index])) else 0. )
                y.append(float(tmp[y_index]) if not np.isnan(float(tmp[y_index])) else 0. )

    x = np.array(x)
    y = np.array(y)

    list_of_tuples = list(zip(x, y))
    
    df = pd.DataFrame(list_of_tuples, 
                  columns = [x_arg_name, y_arg_name])
    
    df = df[df[y_arg_name].notna()]
    df = df[df[y_arg_name] >= 0.]
    return df[x_arg_name], df[y_arg_name]


def calculating_max_res_from_CCstar_dat(dat_file):
    x,y = get_xy(dat_file, x_arg_name, y_arg_name)
    
    CC2, d2 = y[0], x[0]
    CC1, d1 = 0., 0.
    resolution = -100
    i = 0
    while y[i] >= 0.5 and i < len(x):
        CC1, d1 = CC2, d2
        i+=1
        try:
            CC2, d2 = y[i], x[i]
        except:
            return -1000
        if y[i] == 0.5:
            resolution = x[i]
            break
            
    k = round((CC2-CC1)/(d2-d1), 3)
    b = round((CC1*d2-CC2*d1)/(d2-d1), 3)    
    resolution = round((0.5 -b) / k, 3)
    return resolution
    
def max_res_for_pf8(stream_filename, data_resolution):
    try:
        command = f'grep -e indexamajig {stream_filename}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        geometry_file = '/'+re.findall(r"\b\S+\.geom", result)[0]
        
        command = f'grep -e clen {geometry_file}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        clen = float(re.search(r'\d+\.\d+',result).group(0))
        
        command = f'grep -e photon_energy {geometry_file}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        photon_energy = float(re.search(r'\d+',result).group(0))

        wavelength = round(12400. / photon_energy, 3)

        command = f'grep -e res {geometry_file}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        res = float(re.search(r'\d+\.\d+',result).group(0))
        
        max_res_for_peakfinding = int(res * clen * math.tan(2*math.asin(wavelength / (2*data_resolution))))
    except subprocess.CalledProcessError:
        pass
        
    return max_res_for_peakfinding
    
def filling_template(stream_filename, block_name, output, bin_size=2, min_good_pix_count=3, max_res=600):
    os.chdir(output)
    try:
        command = f'grep -e indexamajig {stream_filename}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        geometry_file = '/'+re.findall(r"\b\S+\.geom", result)[0]

        min_num_peaks_for_hit = re.findall(r"\-\-min\-peaks=\d+", result)
        min_num_peaks_for_hit = int(min_num_peaks_for_hit[0].split('=')[-1]) if len(min_num_peaks_for_hit)>0 else 10

        max_num_peaks_for_hit = re.findall(r"\-\-max\-peaks=\d+", result)
        max_num_peaks_for_hit = int(max_num_peaks_for_hit[0].split('=')[-1]) if len(max_num_peaks_for_hit)>0 else 5000
        
        adc_threshold = re.findall(r"\-\-threshold=\d+", result)
        adc_threshold = int(adc_threshold[0].split('=')[-1]) if len(adc_threshold)>0 else 10
        
        minimum_snr = re.findall(r"\-\-min\-snr=\d+\.\d*", result)
        minimum_snr = float(minimum_snr[0].split('=')[-1]) if len(minimum_snr)>0 else 4.5
       
        min_pixel_count = re.findall(r"\-\-min\-pix\-count=\d+", result)
        min_pixel_count = int(min_pixel_count[0].split('=')[-1]) if len(min_pixel_count)>0 else 1

        max_pixel_count = re.findall(r"\-\-max\-pix\-count=\d+", result)
        max_pixel_count = int(max_pixel_count[0].split('=')[-1]) if len(max_pixel_count)>0 else 50
        
        min_res = re.findall(r"\-\-min\-res=\d+", result)
        min_res = int(min_res[0].split('=')[-1]) if len(min_res)>0 else 10

        local_bg_radius = re.findall(r"\-\-local\-bg\-radius=\d+", result)
        local_bg_radius = int(local_bg_radius[0].split('=')[-1]) if len(local_bg_radius)>0 else 4
     
        command = f'grep -e mask_file {stream_filename}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        bad_pixel_map_filename = '/'+re.findall(r"\b\S+\.h5", result)[0]

        command = f'grep -e "mask =" {stream_filename}'
        result = subprocess.check_output(shlex.split(command)).decode('utf-8').strip().split('\n')[0]
        bad_pixel_map_hdf5_path = result.replace(' ','').split('=')[-1]
       
    except subprocess.CalledProcessError:
        pass

    command = f'cp /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf/templates-for-work/template-work.yaml ./template.yaml'
    os.system(command)

    template_data = {"GEOMETRY":geometry_file, "MINPEAKS":min_num_peaks_for_hit, "MAXPEAKS":max_num_peaks_for_hit, "BINSIZE":bin_size, "MASKFILE":bad_pixel_map_filename, "MASKPATH":bad_pixel_map_hdf5_path, "MINGOODPIXCOUNT":min_good_pix_count, "THRESHOLD":adc_threshold, "MINSNR":minimum_snr, "MINPIXCOUNT":min_pixel_count,"MAXPIXCOUNT":max_pixel_count, "LOCALBGRADIUS":local_bg_radius, "MINRES":min_res, "MAXRES":max_res}

    monitor_file = open(f'{block_name}.yaml', 'w')
    with open('template.yaml', 'r') as f:
        src = Template(f.read())
        result = src.substitute(template_data)
        monitor_file.write(result)
    monitor_file.close()
    os.remove('template.yaml')
    
    return os.path.abspath(f'{block_name}.yaml')

def prepare_blocks(blocks):
    d = defaultdict(dict)
    file = open(blocks, 'r')
    for line in file:
        key,template=line.strip().split(':') if len(line.strip().split(':')) > 1 else line.strip().split(':')[0], ''
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
                #print(f,l)
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
    #print(d)
    return d

def binning(run, raw_data_path, output_dir, template, skip_flag):
    
    '''
    run=$1
    inputdir=$2
    outdir=$3
    template=$4
    '''
    logger = logging.getLogger('app')
    output_path = os.path.join(output_dir, run)
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)
    

    if not(skip_flag) or len(glob.glob(os.path.join(output_path, '*.yaml'))) == 0:
        command = 'source /gpfs/cfel/group/cxi/scratch/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf/run_binning_compression.sh {} {} {} {}'.format(run, raw_data_path, output_dir, template)
        
        #print(command)
        logger.info(f'INFO: Execute {command}')
        os.system(command)
    else:
        logger.info(f'INFO: Run {run} was skipped')    

def running_main(blocks_filename, raw_data_path, processed_raw_data_path, output_path, bin_size, min_good_pix_count, forces_template, skip_flag, max_res_value):
    logger = logging.getLogger('app')
    
    d_info = prepare_blocks(blocks_filename)
    folders = os.listdir(processed_raw_data_path)
    
    if forces_template is None:
        templates_folder = os.path.join(output_path, 'templates')
        if not os.path.exists(templates_folder):
            os.mkdir(templates_folder)
            
        for key in d_info:
            folder = os.path.join(processed_raw_data_path, list(filter(lambda element: key in element, folders))[0])
            stream_filename = glob.glob(f'{folder}/**/*.stream', recursive=True)[0] # stream file for parsing for template
            if max_res_value is not None:
                template_name = filling_template(stream_filename, key, templates_folder, bin_size, min_good_pix_count, max_res_value)
                runs = d_info[key]['blocks']
                for run in runs:
                    binning(run, raw_data_path, output_path, template_name, skip_flag)
            else:
                dat_file = glob.glob(f'{folder}/**/*CCstar.dat', recursive=True)[0] if len(glob.glob(f'{folder}/**/*CCstar.dat', recursive=True)) > 0 else ''#CCstar dat file for estimation max res for hits finding
                
                data_resolution = calculating_max_res_from_CCstar_dat(dat_file) if len(dat_file) > 0 else -1000
                
                if data_resolution != -1000:
                    max_res = max_res_for_pf8(stream_filename, data_resolution)
                    
                    template_name = filling_template(stream_filename, key, templates_folder, bin_size, min_good_pix_count, max_res)
                    runs = d_info[key]['blocks']
                    for run in runs:
                        binning(run, raw_data_path, output_path, template_name, skip_flag)
                else:
                    #print(f'Warning: Check {dat_file}')
                    logger.info(f'Warning: Check {dat_file if len(dat_file)>0 else key}')
    else:
        for key in d_info:
            folder = os.path.join(processed_raw_data_path, list(filter(lambda element: key in element, folders))[0])
            runs = d_info[key]['blocks']
            for run in runs:
                binning(run, raw_data_path, output_path, forces_template, skip_flag)
setup_logger()

if __name__ == "__main__":
    args = parse_cmdline_args()
    blocks_filename = args.f
    raw_data_path = args.i
    processed_raw_data_path = args.p
    output_path =  args.o
    bin_size = args.b
    min_good_pix_count = args.n
    forces_template = args.t
    skip_flag = args.s
    max_res_value = args.maxres
    
    if not(os.path.exists(output_path)):
        os.mkdir(output_path)
    
    running_main(blocks_filename, raw_data_path, processed_raw_data_path, output_path, bin_size, min_good_pix_count, forces_template, skip_flag, max_res_value)
    
