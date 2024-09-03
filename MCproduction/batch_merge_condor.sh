# This merges root files together

process_name=idm_dilepton
year=2022_postEE

# Change input directory
BASE_DIRECTORY=/eos/user/e/ecurtis/idmFilesEOS/gridpacks/idm_dilepton_13p6_parameterscan_updatedWidths_CMSSW_12_4_8
               
run_name=$(process_name)_mH$(mH)_mA$(mA)
# Change depending on the year
INPUT_DIR=$(BASE_DIRECTORY)/$(run_name)/Data/$(year)
# Change output directory
OUTPUT_DIR=$(BASE_DIRECTORY)/merged_outputs/$(year)/$(process_name)_$(year)_mH$(mH)_mA$(mA)_merged.root 

Executable = /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/merge_files.sh

# have to do logging on afs768583920
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output = $(home)/logging/merge_outputs_$(tag)_mH$(mH)_mA$(mA)_$(year).out
error = $(home)/logging/merge_outputs_$(tag)_mH$(mH)_mA$(mA)_$(year).err


arguments = $(INPUT_DIR) $(OUTPUT_DIR)


Transfer_Output_Files = ""
Universe = vanilla
#+MaxRuntime = 3600
+JobFlavour = "espresso"

queue mH, mA from /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/newGenproductions/bin/MadGraph5_aMCatNLO/cards/iDMParameterScanUpdatedWidths_mHmA_noLLLNu/cards/13p6/input_arguments.txt
#queue
