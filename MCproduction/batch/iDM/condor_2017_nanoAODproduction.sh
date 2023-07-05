# This file creates all of the gridpacks, then sends them over the the myFiles
# directory on EOS
# Name of the process:
tag = h2h2lPlMnunu_lem_nuemt
scram_version=slc7_amd64_gcc700
CMSSW_version=CMSSW_10_6_19
run_name=$(tag)_BP$(item)
NEVENTS=2500
OUTPATH=root://eosuser.cern.ch//eos/user/e/ecurtis/idmStudyImperial/myFiles/gridpacks/$(tag)/$(run_name)

# arguments 
GRIDPACK=root://eosuser.cern.ch//eos/user/e/ecurtis/idmStudyImperial/myFiles/gridpacks/$(tag)/$(run_name)/$(run_name)_$(scram_version)_$(CMSSW_version)_tarball.tar.xz
FRAGMENT=root://eosuser.cern.ch//eos/user/e/ecurtis/idmStudyImperial/MCproduction/fragments/iDM/general_config.py
Proxy_path = /afs/cern.ch/user/e/ecurtis/cms.proxy

Executable = condor_RunIIFall17_nanAOD.sh

# have to do logging on afs
home=/afs/cern.ch/user/e/ecurtis/idmStudy/MCproduction
output = $(home)/logging/$(tag)_$(ClusterId)_$(item).out
error = $(home)/logging/$(tag)_$(ClusterId)_$(item).err
log = $(home)/logging/$(tag)_$(ClusterId)_$(item).log


arguments = $(Proxy_path) $(GRIDPACK) $(FRAGMENT) $(NEVENTS) $(OUTPATH) $(ClusterId) $(item)

#Transfer_Input_Files = $(GRIDPACK) $(FRAGMENT)
#Transfer_Input_Files = /afs/cern.ch/user/e/ecurtis/cms.proxy 

#Transfer_Input_Files = /afs/cern.ch/user/e/ecurtis/idmStudy/MCproduction/pulist_Fall17.txt
#should_transfer_files = NO
Transfer_Output_Files = ""
# when_to_transfer_output = ON_EXIT
Universe = vanilla
+JobFlavour = "testmatch"

queue 20 in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20)
#queue from seq 1 20 |

