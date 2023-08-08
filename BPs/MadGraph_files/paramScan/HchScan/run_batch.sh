#!/bin/bash
ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

BP=$1
split=$2

run_name=h2h2lPlM

./bin/mg5_aMC /vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/HchScan/${run_name}/MG_script_BP${BP}_mHch_split_${split}.sh

# command line script to run:
# qsub -q hep.q -o /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/log.log -e /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/error.err -l h_rt=24:0:0 -pe hep.pe 4 -t 1-21:1 run_batch.sh h2h2lPlM_lemt

# for BP in 2 5 6; do for split in 1 40 80; do qsub -q hep.q -cwd -l h_rt=24:0:0 -pe hep.pe 4 run_batch.sh ${BP} ${split}; done; done