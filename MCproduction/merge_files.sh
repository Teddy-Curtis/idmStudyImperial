#!/bin/bash

# This is the input directory where all the files are
INPUT_DIR=$1
# where to save them
OUTPUT_DIR=$2
INPUT_DIR=${INPUT_DIR}/*.root

echo ${INPUT_DIR}
echo ${OUTPUT_DIR}

hadd ${OUTPUT_DIR} ${INPUT_DIR}
