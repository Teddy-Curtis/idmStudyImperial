# This is used to send MC production jobs to condor
# This file creates all of the gridpacks, then sends them over the the myFiles
# directory on EOS
# Name of the process:
tag=h2h2lll
scram_version=slc7_amd64_gcc700
CMSSW_version=CMSSW_10_6_28_patch1
run_name=$(tag)_mH$(mH)_mA$(mA)_mHch$(mHch)
NEVENTS=500
OUTPATH=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/$(tag)_parameterscan_updatedWidths_$(CMSSW_version)_differentPTs/$(run_name)
                               
# arguments 
GRIDPACK=root://eosuser.cern.ch//eos/user/e/ecurtis/idmFilesEOS/gridpacks/$(tag)_parameterscan_updatedWidths_$(CMSSW_version)_differentPTs/$(run_name)/$(run_name)_$(scram_version)_$(CMSSW_version)_tarball.tar.xz
FRAGMENT=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/fragments/iDM/central_production_config.py
Proxy_path=/afs/cern.ch/user/e/ecurtis/cms.proxy

#! CHANGE THIS DEPENDING ON WHAT YEAR YOU ARE CREATING MC FOR!!!
Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIIFall17_nanoAOD_condor_central.sh
#Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIIAutumn18_nanoAOD_condor_central.sh
#Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIISummer16_preVFP_nanoAOD_condor_central.sh
#Executable=/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/RunIISummer16_postVFP_nanoAOD_condor_central.sh

# have to do logging on afs
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output = $(home)/logging/MCprod_$(run_name)_$(ClusterId)_differentPTs.out
error = $(home)/logging/MCprod_$(run_name)_$(ClusterId)_differentPTs.err

log = $(home)/logging/MCprod_$(run_name)_$(ClusterId).log


arguments = $(Proxy_path) $(GRIDPACK) $(FRAGMENT) $(NEVENTS) $(OUTPATH) $(run_name)


Transfer_Output_Files = ""
Universe = vanilla
#+JobFlavour = "microcentury"
+MaxRuntime=72000



# for i in {1..100}; do condor_submit condor_production.sh; done

#! CHANGE THIS DEPENDING ON THE MASS OF H!!!
queue mH, mA, mHch from /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/genproductions/bin/MadGraph5_aMCatNLO/cards/iDM_trilepton/mH80/input_arguments.txt