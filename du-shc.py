import os
import sys
import subprocess
import re
import glob
import collections

d = collections.defaultdict(dict)

init = sys.argv[1] #'/asap3/petra3/gpfs/p11/2020/data/11010575/raw/'
volume, cdir = subprocess.check_output(['du', '-shc', init]).strip().decode('utf-8').split('\n')[0].split('\t')
d['Total']['before'] = volume

after = sys.argv[2] #'/asap3/petra3/gpfs/p11/2020/data/11010575/scratch_cc/galchenm/compression/'
volume, cdir = subprocess.check_output(['du', '-shc', after]).strip().decode('utf-8').split('\n')[0].split('\t')
d['Total']['after'] = volume



dirs_init = [os.path.join(init, f) for f in os.listdir(init)]
dirs_after = [os.path.join(after, f) for f in os.listdir(after)]

for dir in dirs_init:
    if os.path.isdir(dir):
        volume, cdir = subprocess.check_output(['du', '-shc', dir]).strip().decode('utf-8').split('\n')[0].split('\t')
        cdir = os.path.basename(cdir)
        d[cdir]['before'] = volume
        d[cdir]['after'] = 0
    
for dir in dirs_after:
    if os.path.isdir(dir):
        volume, cdir = subprocess.check_output(['du', '-shc', dir]).strip().decode('utf-8').split('\n')[0].split('\t')
        cdir = os.path.basename(cdir).split('-')[0]
        d[cdir]['after'] = volume


print('{:^8}     {:^6}     {:^5}'.format('run', 'before', 'after'))
keys = list(d.keys())
keys.sort()
for key in keys:
    print('{:^8}     {:^6}     {:^5}'.format(key, d[key]['before'],d[key]['after']))
    