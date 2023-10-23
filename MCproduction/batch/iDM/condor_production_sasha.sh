# This is used to send MC production jobs to condor
# This file creates all of the gridpacks, then sends them over the the myFiles
# directory on EOS
# Name of the process:
tag=h2h2muPmuM
scram_version=slc7_amd64_gcc700
CMSSW_version=CMSSW_10_6_28_patch1
item=12345
NEVENTS=500
OUTPATH=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/h2h2muPmuM/h2h2muPmuM

# arguments 
GRIDPACK=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/h2h2muPmuM/h2h2muPmuM/h2h2muPmuM_slc7_amd64_gcc700_CMSSW_10_6_28_patch1_tarball.tar.xz
FRAGMENT=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/fragments/iDM/central_production_config.py
Proxy_path=/afs/cern.ch/user/e/ecurtis/cms.proxy

#! CHANGE THIS DEPENDING ON WHAT YEAR YOU ARE CREATING MC FOR!!!
Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIIFall17_nanoAOD_condor_central.sh

# have to do logging on afs
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output=$(home)/logging/$(tag)_$(ClusterId).out
error=$(home)/logging/$(tag)_$(ClusterId).err
log=$(home)/logging/$(tag)_$(ClusterId).log


arguments = $(Proxy_path) $(GRIDPACK) $(FRAGMENT) $(NEVENTS) $(OUTPATH) $(ClusterId) $(item)


Transfer_Output_Files=""
Universe=vanilla
+JobFlavour="workday"

queue

