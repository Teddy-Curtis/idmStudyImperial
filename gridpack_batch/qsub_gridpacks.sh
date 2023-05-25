#!/bin/bash
#$-q hep.q -l h_rt=12:0:0 -e /vols/cms/emc21/idmStudy/gridpack_batch/logging/ -o /vols/cms/emc21/idmStudy/gridpack_batch/logging/
BPNUM=$1

# define the process name here
PROCESS="h2h2lPlMnunu_lem_nuemt"
echo "Making gridpack for process" $PROCESS "for BP" $BPNUM
#CMSSW_version="CMSSW_10_6_27"
#CMSSW_version="CMSSW_9_4_7"
#CMSSW_version="CMSSW_10_2_22"
#CMSSW_version="CMSSW_9_3_12_patch2"
CMSSW_version="CMSSW_10_6_19"
#scram_version="slc7_amd64_gcc700"
#scram_version="slc6_amd64_gcc630"
#scram_version="slc6_amd64_gcc700"
#scram_version="slc6_amd64_gcc630"
scram_version="slc7_amd64_gcc700"

ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/genproductions/bin/MadGraph5_aMCatNLO

./gridpack_generation.sh ${PROCESS}_BP${BPNUM} cards/iDM/${PROCESS}/${PROCESS}_BP${BPNUM} local ALL ${scram_version} ${CMSSW_version} ${PROCESS}

# for BP in 8 10 12 13 14 18 19 20 21 24; do qsub qsub_gridpacks.sh $BP; done
# for BP in 1 2 3 4 5 6 7 9 11 15 16 17; do qsub qsub_gridpacks.sh $BP; done
# for BP in {1..20}; do qsub qsub_gridpacks.sh $BP; done