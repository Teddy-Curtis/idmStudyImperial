#!/bin/bash
#$-q hep.q -l h_rt=8:0:0 -e /vols/cms/emc21/idmStudy/MCproduction/logging/ -o /vols/cms/emc21/idmStudy/MCproduction/logging/
BPNUM=$1
run_name="h2h2lPlM_lem"
CMSSW_version="CMSSW_10_2_22"
scram_version="slc6_amd64_gcc700"
nevents=10
ncpus=1

# Now get the arguments
tag="${run_name}_BP${BPNUM}"
gridpack="/vols/cms/emc21/idmStudy/myFiles/gridpacks/${run_name}_${CMSSW_version}/${tag}/${tag}_${scram_version}_${CMSSW_version}_tarball.tar.xz"
fragment="/vols/cms/emc21/idmStudy/MCproduction/fragments/iDM/general_config.py"
output_folder="/vols/cms/emc21/idmStudy/myFiles/gridpacks/${run_name}_${CMSSW_version}/${tag}"

ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/MCproduction


/vols/cms/emc21/idmStudy/MCproduction/RunInSteps.sh ${gridpack} ${fragment} ${nevents} ${ncpus} ${output_folder} #${CMSSW_version} ${scram_version}
# for BP in 8 10 12 13 14 18 19 20 21 24; do qsub qsub_h2h2lPlM_lem.sh $BP; done
