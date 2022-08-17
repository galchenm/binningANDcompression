import os
import sys
import numpy as np
import h5py as h5

constant_base = 8

def decompressor(x):
    x_sign = np.sign(x)
    if x == 0:
        return 0
    x = x_sign * x
    power = x // constant_base
    #print('power = ', power)
    value = x % constant_base
    value_bin = "{0:b}".format(int(value))
    #print('value_bin = ', value_bin)
    prev_x_bin = 10**power + int(value_bin)*10**(power-2)
    #print('prev_x_bin = ', prev_x_bin)
    prev_x = x_sign * int(str(prev_x_bin), 2)
    #print('prev_x = ',prev_x)
    return prev_x

def decompressor_3bits(x):
    x_sign = np.sign(x)
    if x == 0:
        return 0
    x = x_sign * x
    power = x // constant_base
    print('power = ', power)
    value = x % constant_base
    value_bin = "{0:b}".format(int(value))
    print('value_bin = ', value_bin)
    if power < 3:
        return x_sign * value
    prev_x_bin = 10**power + int(value_bin)*10**(power-2)
    print('prev_x_bin = ', prev_x_bin)
    prev_x = x_sign * int(str(prev_x_bin), 2)
    print('prev_x = ',prev_x)
    return prev_x


def decompressor_4bits(x):
    x_sign = np.sign(x)
    if x == 0:
        return 0
    x = x_sign * x
    power = x // constant_base
    print('power = ', power)
    value = x % constant_base
    value_bin = "{0:b}".format(int(value))
    print('value_bin = ', value_bin)
    if power < 4:
        return x_sign * value
    prev_x_bin = 10**power + int(value_bin)*10**(power-2)
    print('prev_x_bin = ', prev_x_bin)
    prev_x = x_sign * int(str(prev_x_bin), 2)
    print('prev_x = ',prev_x)
    return prev_x

v_decompressor = np.vectorize(decompressor_4bits)

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

with h5.File(file_cxi, mode) as f:
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