import os
import sys
import numpy as np
import h5py as h5


file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]
N = float(sys.argv[4])
lim_up = sys.argv[5]
outputpath = sys.argv[6]

if lim_up != str(None):
    lim_up = int(lim_up)
else:
    lim_up = None

if outputpath != str(None):
    out_file = os.path.join(outputpath, os.path.basename(file_cxi))
    mode = 'w'
else:
    out_file = file_cxi
    mode = 'a'

with h5.File(out_file, mode) as f:
    if mode == 'a':
        data = f[path_to_data_cxi]
    else:
        data = h5.File(file_cxi, 'r')[path_to_data_cxi]
    shape_data = data.shape[1:]
    num = data.shape[0]
    initShape = (1,) + shape_data
    maxShape = (num,) + shape_data
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = (np.round(data[0,]/N,0)).astype(np.int32) if lim_up is None else np.where(data[0,] < lim_up, (np.round(data[0,]/N,0)).astype(np.int32), lim_up)
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = (np.round(data[i,]/N,0)).astype(np.int32) if lim_up is None else np.where(data[i,] < lim_up, (np.round(data[i,]/N,0)).astype(np.int32), lim_up)