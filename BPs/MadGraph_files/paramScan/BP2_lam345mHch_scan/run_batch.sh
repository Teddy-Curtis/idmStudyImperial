#!/bin/bash
ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

split=$1
lam=$2

run_name=h2h2lPlM

./bin/mg5_aMC /vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/BP2_lam345mHch_scan/${run_name}/MG_script_BP2_mHch_split_${split}_lam345_${lam}.sh

# command line script to run:
# qsub -q hep.q -o /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/log.log -e /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/error.err -l h_rt=24:0:0 -pe hep.pe 4 -t 1-21:1 run_batch.sh h2h2lPlM_lemt

# for split in 1 40 80; do for lam in -1 0 1 2; do qsub -q hep.q -cwd -l h_rt=24:0:0 -pe hep.pe 4 run_batch.sh ${split} ${lam}; done; done