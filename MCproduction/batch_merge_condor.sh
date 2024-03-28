# This merges root files together

process_name=h2h2lPlMnunu
year=Summer16_preVFPData

# Change input directory
BASE_DIRECTORY=/eos/user/e/ecurtis/idmFilesEOS/gridpacks/$(process_name)_parameterscan_updatedWidths_mH$(mH)_CMSSW_10_6_28_patch1_newRunCard
run_name=$(process_name)_mH$(mH)_mA$(mA)_mHch$(mHch)
# Change depending on the year
INPUT_DIR=$(BASE_DIRECTORY)/$(run_name)/Data/$(year)
# Change output directory
OUTPUT_DIR=$(BASE_DIRECTORY)/merged_outputs/$(year)/$(process_name)_mH$(mH)_mA$(mA)_mHch$(mHch)_merged.root 

Executable = /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/merge_files.sh

# have to do logging on afs768583920
home=/afs/cern.ch/user/e/ecurtis/idmStudyImperial
output = $(home)/logging/merge_outputs_$(tag)_mH$(mH)_mA$(mA)_mHch$(mHch).out
error = $(home)/logging/merge_outputs_$(tag)_mH$(mH)_mA$(mA)_mHch$(mHch).err


arguments = $(INPUT_DIR) $(OUTPUT_DIR)


Transfer_Output_Files = ""
Universe = vanilla
#+MaxRuntime = 3600
+JobFlavour = "espresso"

queue mH, mA, mHch from /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/genproductions/bin/MadGraph5_aMCatNLO/cards/iDMParameterScanUpdatedWidths/mH80/input_arguments.txt
#queue