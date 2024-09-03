#!/bin/bash

process_name=h2h2lPlM
# Change input directory
BASE_DIRECTORY=/eos/user/e/ecurtis/idmFilesEOS/gridpacks/h2h2lPlM_parameterscan_updatedWidths_mH80_CMSSW_10_6_28_patch1_newRunCard
mH=80



mA=100
mHch=130
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}

mA=100
mHch=190
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}

mA=110
mHch=120
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}

mA=110
mHch=140
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}

mA=110
mHch=160
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}

mA=140
mHch=160
run_name=${process_name}_mH${mH}_mA${mA}_mHch${mHch}
# Change depending on the year
INPUT_DIR=${BASE_DIRECTORY}/${run_name}/Data/Fall2017Data
# Change output directory
OUTPUT_DIR=${BASE_DIRECTORY}/merged_outputs/${process_name}_mH${mH}_mA${mA}_mHch${mHch}_merged.root 
./merge_files.sh ${INPUT_DIR} ${OUTPUT_DIR}