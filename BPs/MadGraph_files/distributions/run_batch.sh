#!/bin/bash
ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/MG5_aMC_v2_6_7/

run_name=$1

./bin/mg5_aMC /vols/cms/emc21/idmStudy/MadGraph_files/distributions/${run_name}/BP${SGE_TASK_ID}/run_script.sh

# command line script to run:
# qsub -q hep.q -o /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/log.log -e /vols/cms/emc21/idmStudy/MadGraph_files/distributions/h2h2lPlM_lemt/error.err -l h_rt=24:0:0 -pe hep.pe 4 -t 1-21:1 run_batch.sh h2h2lPlM_lemt