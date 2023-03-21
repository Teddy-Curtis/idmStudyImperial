#!/bin/bash


if (( "$#" != "5" ))
    then
    echo $# $*
    echo "Input parameter needed: <gridpack> <fragment> <nevts> <nthreads> <outpath>"
    echo "./run_wmNANOAODGEN_RunIIFall17_changedCMSSW.sh "
    exit
fi


i=1
GRIDPACK=${!i}; i=$((i+1))
FRAGMENT=${!i}; i=$((i+1))
NEVENTS=${!i}; i=$((i+1))
NTHREADS=${!i}; i=$((i+1))
OUTPATH=${!i}; i=$((i+1))

# This runs differently on lx02 batch than it does on condor. On condor it 
# runs on a separate machine so when it creates a CMSSW env it is on that machine
# and it goes when the program stops. Whereas on lx02, it runs in the directory 
# so the CMSSW folder: 1. doesn't go, 2. If I run multiple qsub at a time then 
# they all use the same folders and it breaks.
CURRENT_DIR=`pwd`
echo ${CURRENT_DIR}
if [ "${CURRENT_DIR:0:5}" = "/vols" ]; then
    echo "On Imperial servers therefore changing the batch directory to $OUTPATH"
    cd $OUTPATH
else
    echo "Running on CERN servers, therefore not changing directory from the condor machine"
fi


#!/bin/bash
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_27/src ] ; then 
 echo release CMSSW_10_6_27 already exists
else
scram p CMSSW CMSSW_10_6_27
fi
cd CMSSW_10_6_27/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd ../../
seed=$(date +%s%N)
cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--fileout file:mc_NANOAODGEN.root \
--mc \
--eventcontent NANOAODGEN \
--datatier NANOAOD \
--conditions 106X_mc2017_realistic_v9 \
--beamspot Realistic25ns13TeVEarly2017Collision \
--step LHE,GEN,NANOGEN \
--nThreads ${NTHREADS} \
--geometry DB:Extended \
--era Run2_2017,run2_nanoAOD_106Xv2 \
--python_filename mc_NANOAODGEN.py \
--no_exec \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))" \
-n ${NEVENTS} || exit $? ; 


cmsRun mc_NANOAODGEN.py | tee log_mc_NANOAODGEN.txt

OUTTAG=$(echo $JOBFEATURES | sed "s|_[0-9]*$||;s|.*_||")

if [ -z "${OUTTAG}" ]; then
    OUTTAG=$(md5sum *.root | head -1 | awk '{print $1}')
fi

echo "Using output tag: ${OUTTAG}"
mkdir -p ${OUTPATH}
ls 
for file in *.root; do 
    mv $file $OUTPATH/$(echo $file | sed "s|.root|_${OUTTAG}.root|g")
done
for file in *.txt; do 
    mv $file $OUTPATH/$(echo $file | sed "s|.root|_${OUTTAG}.txt|g")
done

# Now delete the CMSSW folder to save space
if [ "${CURRENT_DIR:0:5}" = "/vols" ]; then
    echo "On Imperial servers therefore deleting the CMSSW folder"
    rm -rf CMSSW_10_6_27
else
    echo "Running on CERN servers, therefore don't need to delete the CMSSW folder"
fi
