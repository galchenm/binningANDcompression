import os
import sys
import numpy as np
import h5py as h5

def rounding_four_bits(x): # constant_base = 8 only!!!
    x_sign = np.sign(x)
    print(x)
    if x == 0:
        return 0
    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    offset = len(x_bin) - 1
    if len(x_bin) < 5:
        return x_sign * x
    first4bits = int(x_bin) // 10 ** (offset - 3)
    value_bin = first4bits * 10 ** (offset - 3)
    value = int(str(value_bin), 2)
    return x_sign * value

def truncating_N_bits(x, N): # constant_base = 8 only!!!
    x_sign = np.sign(x)
    print(x)
    if x == 0:
        return 0
    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    offset = len(x_bin) - 1
    if len(x_bin) < N+1:
        return x_sign * x
    firstNbits = int(x_bin) // 10 ** (offset - (N-1))
    value_bin = firstNbits * 10 ** (offset - (N-1))
    value = int(str(value_bin), 2)
    return x_sign * value

def rounding_N_bits(x, N): # constant_base = 8 only!!!
    x_sign = np.sign(x)
    if x == 0:
        return 0
    x = x_sign * x
    x_bin = "{0:b}".format(int(x))
    print(x_bin)
    offset = len(x_bin) - 1
    if len(x_bin) < N+1:
        return x_sign * x
    Nbit = int(x_bin[N])
    firstNbits = int(x_bin) // 10 ** (offset - (N-1))
    print(firstNbits)
    value_bin = firstNbits * 10 ** (offset - (N-1))
    print(Nbit)
    value = int(str(value_bin), 2) + int(str(Nbit*10 ** (offset - N+1)),2)
    return x_sign * value

v_compressor = np.vectorize(rounding_four_bits)

file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]

outputpath = sys.argv[4]
lim_up = sys.argv[5]

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
    tmp = data[0,] if lim_up is None else np.where(data[0,] < lim_up, data[0,], lim_up)
    d[0,] = v_compressor(tmp.astype(np.int))
    for i in range(num):
        d.resize((i+1,) + shape_data)
        tmp = data[i,] if lim_up is None else np.where(data[i,] < lim_up, data[i,], lim_up)
        d[i,] = v_compressor(tmp.astype(np.int))