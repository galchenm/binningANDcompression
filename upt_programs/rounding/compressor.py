import os
import sys
import numpy as np
import h5py as h5
import re

def compressor(x):
    sign_x = np.sign(x)
    x = sign_x * x
    binary_x = "{0:b}".format(x)
    exponent = len(binary_x) - 1
    binary_exponent = "{0:b}".format(exponent)
    if exponent < 4:
        return sign_x * x
    first_4bits = binary_x[0:4]
    binary_mantissa = first_4bits[1:]
    compressed_value = binary_exponent + binary_mantissa
    return sign_x*int(compressed_value, 2)


v_compressor = np.vectorize(compressor)

file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]
outputpath = sys.argv[4]

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
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int8, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = v_compressor(data[0,])
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = v_compressor(data[i,])