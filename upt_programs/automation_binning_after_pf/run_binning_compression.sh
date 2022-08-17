#!/bin/sh

module load anaconda3/5.2

run=$1
inputdir=$2
outdir=$3
template=$4

if [[ ! -e $outdir/${run} ]]; then
    mkdir $outdir/${run}
elif [[ ! -d $outdir/${run} ]]; then
    echo "$outdir already exists but is not a directory" 1>&2
fi

cd $outdir/${run}


SLURMFILE="${run}.sh"
#find /asap3/petra3/gpfs/p11/2020/data/11010575/raw/${run} -name "*_data_*.h5" > files.lst
#find ${inputdir}/${run} -name "*_data_*.h5" > ${outdir}/${run}/files.lst

ls -v ${inputdir}/${run}/*_data_*.h5 > ${outdir}/${run}/files.lst
NUMLINES=$(wc -l < "${outdir}/${run}/files.lst")

#echo $NUMLINES
#t=$(echo "$((0.05*$NUMLINES))"| awk '{printf("%d\n",$1 + 12.5)}') # Size of job chunks 0.5 ---> 12.5

#echo $t

chmod ugo+wr ${template}
cp ${template} $outdir/${run}/monitor.yaml
chmod ugo+r $outdir/${run}/monitor.yaml


sed -i "s/RUN/$run/" $outdir/${run}/monitor.yaml

echo "#!/bin/sh" > $SLURMFILE
echo >> $SLURMFILE

#echo "#SBATCH --partition=upex" >> $SLURMFILE  # Set your partition here
echo "#SBATCH --partition=all,upex,cfel,cfel-cdi" >> $SLURMFILE  # Set your partition here
echo "#SBATCH --time=24:00:00" >> $SLURMFILE
echo "#SBATCH --nodes=1" >> $SLURMFILE
echo >> $SLURMFILE

echo "#SBATCH --chdir   ${outdir}/${run}" >> $SLURMFILE
echo "#SBATCH --job-name  ${run}-cheetah" >> $SLURMFILE
echo "#SBATCH --output    ${outdir}/${run}/slurm.out" >> $SLURMFILE
echo "#SBATCH --error     ${outdir}/${run}/slurm.err" >> $SLURMFILE
echo "#SBATCH --nice=10" >> $SLURMFILE

echo >> $SLURMFILE

echo "module load anaconda3/5.2" >> $SLURMFILE
#echo "export PATH=$PATH:/asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/bin/" >> $SLURMFILE
#echo "export PYTHONPATH=$PYTHONPATH:/asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/lib/python3.6/site-packages/" >> $SLURMFILE
#echo "mpirun -np 30 /asap3/petra3/gpfs/p11/2020/data/11009046/scratch_cc/alexandra/cheetah/bin/om_monitor.py ${outdir}/${run}/files.lst" >> $SLURMFILE

echo "source /home/atolstik/miniforge3/envs/om-dev//bin/activate" >> $SLURMFILE
echo "mpirun -np 11 om_monitor.py ${outdir}/${run}/files.lst" >> $SLURMFILE

sbatch $SLURMFILE

cd /gpfs/cfel/group/cxi/scratch/data/2020/EXFEL-2019-Schmidt-Mar-p002450/scratch/galchenm/scripts_for_work/binningANDcompression/upt_programs/automation_binning_after_pf