#!/bin/bash
#$-q hep.q -l h_rt=4:0:0 -e /vols/cms/emc21/idmStudy/gridpack_batch/logging/ -o /vols/cms/emc21/idmStudy/gridpack_batch/logging/
BPNUM=$1
#CMSSW_version="CMSSW_10_6_27"
CMSSW_version="CMSSW_9_4_7"
#scram_version="slc7_amd64_gcc700"
scram_version="slc6_amd64_gcc630"

ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/genproductions/bin/MadGraph5_aMCatNLO

./gridpack_generation.sh h2h2lPlM_lem_BP${BPNUM} cards/iDM/h2h2lPlM_lem/h2h2lPlM_lem_BP${BPNUM} local ALL ${scram_version} ${CMSSW_version}

# for BP in 8 10 12 13 14 18 19 20 21 24; do qsub qsub_gridpacks.sh $BP; done

