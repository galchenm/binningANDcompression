import os
import sys
import numpy as np
import h5py as h5

def power2_upt(I, N):
    binary_repr_vec = np.vectorize(bin)
    binary_len = np.vectorize(len)
    Ib = binary_repr_vec(I)
    f_neg = lambda x : 1 if '-' == x[0] else 0
    bin_f_neg = np.vectorize(f_neg)
    k = bin_f_neg(Ib)
    len_Ib = binary_len(Ib)
    k_flat = k.ravel()
    f2k = lambda x,k: int(x[2+k]) if len(x)>=3+k else 0
    Ib_2plk = np.array(list(map(f2k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f3k = lambda x,k: int(x[3+k]) if len(x)>=4+k else 0
    Ib_3plk = np.array(list(map(f3k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f4k = lambda x,k: int(x[4+k]) if len(x)>=5+k else 0
    Ib_4plk = np.array(list(map(f4k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    f5k = lambda x,k: int(x[5+k]) if len(x)>=6+k else 0
    Ib_5plk = np.array(list(map(f5k, Ib.ravel(), k_flat))).reshape(Ib.shape)
    #tmpI = np.where((I == 0) | (len_Ib < N+k) | ((len_Ib == N + k) &  (Ib_3plk == 0)) , 0, np.where(((len_Ib == N + k) &  (Ib_2plk == 1)), ((-1) ** k) * 2**(N-2), ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k )) * Ib_4plk + (2. ** (len_Ib - 5 - k)) * Ib_5plk)))
    tmpI = np.where((I == 0) | (len_Ib < N+k) , 0, np.where((len_Ib == N + k), ((-1) ** k) * 2**(N-2), ((-1) ** k) * ((2. ** (len_Ib - 3 - k)) * Ib_2plk + (2. ** (len_Ib - 4 - k)) * Ib_3plk + (2. ** (len_Ib - 5 - k )) * Ib_4plk + (2. ** (len_Ib - 5 - k)) * Ib_5plk)))
    I = tmpI.astype(I.dtype)
    return I

file_cxi = sys.argv[1]
path_to_data_cxi = sys.argv[2]
path_to_data = sys.argv[3]
N = int(sys.argv[4]) + 2 
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
    tmp = data[0,] if lim_up is None else np.where(data[0,] < lim_up, data[0,], lim_up)
    d[0,] = power2_upt(tmp.astype(np.int), N).astype(np.int32)
    
    for i in range(num):
        d.resize((i+1,) + shape_data)
        tmp = data[i,] if lim_up is None else np.where(data[i,] < lim_up, data[i,], lim_up)
        d[i,] = power2_upt(tmp.astype(np.int), N).astype(np.int32)

