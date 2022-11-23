#!/bin/bash
ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/MG5_aMC_v2_6_7/

run_name=$1

./bin/mg5_aMC /vols/cms/emc21/idmStudy/MadGraph_files/BPs/runs/${run_name}/BP${SGE_TASK_ID}/run_script.sh

# Command to run this:
# qsub -q hep.q -o /vols/cms/emc21/idmStudy/MadGraph_files/BPs/runs/hP_allallall/log.log -e /vols/cms/emc21/idmStudy/MadGraph_files/BPs/runs/hP_allallall/error.err -l h_rt=3:0:0 -pe hep.pe 2 -t 1-21:1 run_batch.sh hP_allallall