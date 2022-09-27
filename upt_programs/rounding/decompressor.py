import os
import sys
import numpy as np
import h5py as h5
import re

def decompressor(x):
    sign_x = np.sign(x)
    x = sign_x * x
    binary_x = "{0:b}".format(x)
    if len(binary_x) < 4:
        return sign_x * x
    binary_mantissa = binary_x[-3:]
    binary_exponent = binary_x[:len(binary_x)-3]
    exponent = int(binary_exponent, 2) + 1
    binary_blank_value = '0' * exponent
    binary_value = re.sub(r'^.{0,4}', '1' + binary_mantissa, binary_blank_value)
    decompressed_value = int(str(binary_value), 2)
    return sign_x * decompressed_value

v_decompressor = np.vectorize(decompressor)

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
    d = f.create_dataset(path_to_data, initShape, maxshape=maxShape, dtype=np.int32, chunks=initShape, compression="gzip", compression_opts=6, shuffle=True)
    
    d[0,] = v_decompressor(data[0,])
    for i in range(num):
        d.resize((i+1,) + shape_data)
        d[i,] = v_decompressor(data[i,])