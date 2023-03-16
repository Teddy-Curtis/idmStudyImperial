#!/bin/bash
#$-q hep.q -l h_rt=8:0:0 -e /vols/cms/emc21/idmStudy/MCproduction/logging/ -o /vols/cms/emc21/idmStudy/MCproduction/logging/
BPNUM=$1
run_name="h2h2lPlM_lem"
nevents=30000
ncpus=1

# Now get the arguments
tag="${run_name}_BP${BPNUM}"
gridpack="/vols/cms/emc21/idmStudy/myFiles/gridpacks/${run_name}/${tag}/${tag}_slc7_amd64_gcc700_CMSSW_10_6_27_tarball.tar.xz"
fragment="/vols/cms/emc21/idmStudy/MCproduction/fragments/iDM/general_config.py"
output_folder="/vols/cms/emc21/idmStudy/myFiles/gridpacks/${run_name}/${tag}"

ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/MCproduction

./RunIIFall17_AODSIMGEN.sh ${gridpack} ${fragment} ${nevents} ${ncpus} ${output_folder}
# for BP in 8 10 12 13 14 18 19 20 21 24; do qsub qsub_h2h2lPlM_lem.sh $BP; done
