# This is used to send MC production jobs to condor
# This file creates all of the gridpacks, then sends them over the the myFiles
# directory on EOS
# Name of the process:
tag=h2h2lPlM
scram_version=slc7_amd64_gcc700
CMSSW_version=CMSSW_10_6_28_patch1
run_name=$(tag)_mH$(mH)_mA$(mA)_mHch$(mHch)
NEVENTS=500
OUTPATH=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/$(tag)_parameterscan_updatedWidths_mH$(mH)_$(CMSSW_version)/$(run_name)

# arguments 
GRIDPACK=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/$(tag)_parameterscan_updatedWidths_mH$(mH)_$(CMSSW_version)/$(run_name)/$(run_name)_$(scram_version)_$(CMSSW_version)_tarball.tar.xz
FRAGMENT=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/fragments/iDM/central_production_config.py
Proxy_path=/afs/cern.ch/user/e/ecurtis/cms.proxy

#! CHANGE THIS DEPENDING ON WHAT YEAR YOU ARE CREATING MC FOR!!!
Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIIFall17_nanoAOD_condor_central.sh

# have to do logging on afs
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output = $(home)/logging/$(tag)_$(run_name)_$(ClusterId).out
error = $(home)/logging/$(tag)_$(run_name)_$(ClusterId).err
#log = $(home)/logging/$(tag)_$(run_name)_$(ClusterId).log


arguments = $(Proxy_path) $(GRIDPACK) $(FRAGMENT) $(NEVENTS) $(OUTPATH)


Transfer_Output_Files = ""
Universe = vanilla
#+JobFlavour = "microcentury"
+MaxRuntime=36000

# for i in {1..100}; do condor_submit condor_production.sh; done

#! CHANGE THIS DEPENDING ON THE MASS OF H!!!
queue mH, mA, mHch from /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/genproductions/bin/MadGraph5_aMCatNLO/cards/iDMParameterScanUpdatedWidths/mH80/input_arguments.txt