import os
import sys
import numpy as np
import h5py as h5
import re
import glob

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
v_compressor = np.vectorize(compressor)

input_path = sys.argv[1]
path_to_data_cxi = sys.argv[2]

files_cxi = glob.glob(os.path.join(input_path, '*h5'))
print(files_cxi)

results = {}

for file_cxi in files_cxi:
    file = h5.File(file_cxi, 'r')
    data = file[path_to_data_cxi]
    print(file_cxi)
    num = data.shape[0]
    results[file_cxi] = []
    for i in range(num):
        d_compressed = v_compressor(data[i,])
        d_decompressed = v_decompressor(d_compressed)
        res = (d_decompressed==data[i,]).all()
        results[file_cxi].append(res)
        print(i,res) 
    file.close()

print(results)    