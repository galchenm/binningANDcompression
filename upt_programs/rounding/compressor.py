import os
import sys
import numpy as np
import h5py as h5

constant_base = 8 #4

def compressor(x):
    x_sign = np.sign(x)
    if x == 0:
        return 0
    #print('x=', x)
    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    #print('x_bin = ', x_bin)
    offset = len(x_bin) - 1
    #print('offset = ', offset)
    first3bits = int(x_bin) // 10 ** (offset - 2)
    #print('first3bits = ', first3bits)
    value_bin = first3bits % 100
    #print('value_bin = ', value_bin)
    value = int(str(value_bin), 2)
    #print('value = ', value)
    #print('new value = ', x_sign * (constant_base * offset + value))
    return x_sign * (constant_base * offset + value)

def compressor_three_bits(x): # constant_base = 8 only!!!
    x_sign = np.sign(x)
    if x == 0:
        return 0
    #print('x=', x)
    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    #print('x_bin = ', x_bin)
    offset = len(x_bin) - 1
    #print('offset = ', offset)
    if len(x_bin) < 4:
        return x_sign * (constant_base * offset + x)
    first3bits = int(x_bin) // 10 ** (offset - 2)
    #print('first3bits = ', first3bits)
    value_bin = first3bits % 100
    #value = int(str(int(first3bits)), 2)
    value = int(str(value_bin), 2)
    #print('value = ', value)
    #print('new value = ', x_sign * (constant_base * offset + value))
    return x_sign * (constant_base * offset + value)

def compressor_four_bits(x): # constant_base = 8 only!!!
    x_sign = np.sign(x)
    if x == 0:
        return 0

    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    offset = len(x_bin) - 1
    if len(x_bin) < 5:
        return x_sign * (constant_base * offset + x)
    first3bits = int(x_bin) // 10 ** (offset - 3)
    value_bin = first3bits % 1000
    #value = int(str(int(first3bits)), 2)
    value = int(str(value_bin), 2)
    return x_sign * (constant_base * offset + value)


v_compressor = np.vectorize(compressor_four_bits)

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