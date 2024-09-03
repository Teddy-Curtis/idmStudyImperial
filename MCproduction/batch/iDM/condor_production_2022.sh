# This is used to send MC production jobs to condor
# This file creates all of the gridpacks, then sends them over the the myFiles
# directory on EOS
# Name of the process:
tag=idm_dilepton
scram_version=el8_amd64_gcc10
CMSSW_version=CMSSW_12_4_8
run_name=$(tag)_mH$(mH)_mA$(mA)
NEVENTS=500
OUTPATH=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/idm_dilepton_13p6_parameterscan_updatedWidths_CMSSW_12_4_8/$(run_name)
                               
# arguments 
GRIDPACK=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/idm_dilepton_13p6_parameterscan_updatedWidths_CMSSW_12_4_8/$(run_name)/$(run_name)_$(scram_version)_$(CMSSW_version)_tarball.tar.xz
FRAGMENT=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/fragments/iDM/central_production_config_2022.py
Proxy_path=/afs/cern.ch/user/e/ecurtis/cms.proxy

#! CHANGE THIS DEPENDING ON WHAT YEAR YOU ARE CREATING MC FOR!!!
#Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/run3_2022_nanoAOD.sh
Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/run3_2022_EE_nanoAOD.sh

# have to do logging on afs
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output = $(home)/logging/MCprod_$(run_name)_$(ClusterId)_testEl8_CMSSW_12_4_8_fixedPythiaArgs.out
error = $(home)/logging/MCprod_$(run_name)_$(ClusterId)_testEl8_CMSSW_12_4_8_fixedPythiaArgs.err
log = $(home)/logging/MCprod_$(run_name)_$(ClusterId)_testEl8_CMSSW_12_4_8_fixedPythiaArgs.log


arguments = $(Proxy_path) $(GRIDPACK) $(FRAGMENT) $(NEVENTS) $(OUTPATH) $(run_name)


Transfer_Output_Files = ""
Universe = vanilla
#+JobFlavour = "tomorrow"
+MaxRuntime=108000

#! version
MY.WantOS = "el8"


# for i in {1..50}; do condor_submit condor_production_2022.sh; done

#! CHANGE THIS DEPENDING ON THE MASS OF H!!!
queue mH, mA from /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/newGenproductions/bin/MadGraph5_aMCatNLO/cards/iDMParameterScanUpdatedWidths_mHmA_noLLLNu/cards/13p6/input_arguments.txt
