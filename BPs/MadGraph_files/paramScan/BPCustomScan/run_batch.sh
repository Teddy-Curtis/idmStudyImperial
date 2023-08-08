#!/bin/bash
ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

split=$1
lam=$2

dir=/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/BPCustomScan
run_name=h2h2lPlMnunu

./bin/mg5_aMC ${dir}/${run_name}/MG_script_BP22_mHch_split_${split}_lam345_${lam}.sh

mv ${dir}/run_batch.sh.e${JOB_ID} ${dir}/${run_name}/${run_name}_BP22_mHch_split_${split}_lam345_${lam}/.
mv ${dir}/run_batch.sh.o${JOB_ID} ${dir}/${run_name}/${run_name}_BP22_mHch_split_${split}_lam345_${lam}/.
# command line script to run:
# qsub -q hep.q -o /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/log.log -e /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/error.err -l h_rt=24:0:0 -pe hep.pe 4 -t 1-21:1 run_batch.sh h2h2lPlM_lemt

# for split in 1 40 80; do for lam in -1 0.0001 1 2; do qsub -q hep.q -cwd -l h_rt=24:0:0 -pe hep.pe 4 run_batch.sh ${split} ${lam}; done; done