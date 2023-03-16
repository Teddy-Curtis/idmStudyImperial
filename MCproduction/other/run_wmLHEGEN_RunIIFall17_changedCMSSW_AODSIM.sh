#!/bin/bash


if (( "$#" != "5" ))
    then
    echo $# $*
    echo "Input parameter needed: <gridpack> <fragment> <nevts> <nthreads> <outpath>"
    echo "./run_wmLHEGEN_RunIIFall17_changedCMSSW.sh "
    exit
fi


i=1
GRIDPACK=${!i}; i=$((i+1))
FRAGMENT=${!i}; i=$((i+1))
NEVENTS=${!i}; i=$((i+1))
NTHREADS=${!i}; i=$((i+1))
OUTPATH=${!i}; i=$((i+1))

#!/bin/bash
export SCRAM_ARCH=slc7_amd64_gcc700
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_19/src ] ; then 
 echo release CMSSW_10_6_19 already exists
else
scram p CMSSW CMSSW_10_6_19
fi
cd CMSSW_10_6_19/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd ../../
seed=$(date +%s)
cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--fileout file:wmLHEGEN.root \
--mc \
--eventcontent NANOAODGEN \
--datatier NANOAOD \
--conditions 106X_mcRun2_asymptotic_v15 \
--beamspot Realistic25ns13TeVEarly2017Collision \
--step LHE,GEN,NANOGEN \
--nThreads ${NTHREADS} \
--geometry DB:Extended \
--era Run2_2017,run2_nanoAOD_106Xv1 \
--python_filename wmLHEGEN.py \
--no_exec \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--customise_commands="process.add_(cms.Service('InitRootHandlers', EnableIMT = cms.untracked.bool(False)))" \
-n ${NEVENTS} || exit $? ; 


cmsRun wmLHEGEN.py | tee log_wmLHEGEN.txt

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
