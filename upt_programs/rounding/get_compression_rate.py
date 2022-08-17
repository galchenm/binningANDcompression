import os
import sys
import glob
import subprocess
import re

path = sys.argv[1]
h5path = 'data'

h5Files = glob.glob(os.path.join(path, '*.h5'))

if len(h5Files) != 0:
    common_prefix = os.path.commonprefix(h5Files)
    for f in h5Files:
        
        datatype = os.popen(f'/opt/hdf5/hdf5-1.10.6/bin/h5dump -Hp {f} | grep data -A 10 | grep DATATYPE').read()
        datatype = re.search(r'\w+LE',datatype).group().replace('H5T_STD_','').replace('H5T_IEEE_','').replace('LE','')
        datatype = datatype.replace('DATATYPE','').strip()
        cr = os.popen(f'/opt/hdf5/hdf5-1.10.6/bin/h5dump -Hp {f} | grep data -A 10 | grep COMPRESSION').read()
        cr = re.search(r'\d+.\d+:\d+ COMPRESSION',cr).group()
        cr = re.search(r'\d+.\d+',cr).group()
        compression_type = os.path.basename(f.replace(common_prefix,'')).split('.')[0].replace('_',',')
        print(compression_type, ' - ', cr, ' - ', datatype)