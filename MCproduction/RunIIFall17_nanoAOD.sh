#!/bin/bash
start=`date +%s`

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

SCRAM_ARCH=slc7_amd64_gcc700; export SCRAM_ARCH
scram arch


export X509_USER_PROXY=/home/hep/emc21/cms.proxy

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

# --------------------------------------------LHE, GEN------------------------------------------------------
#!/bin/bash

source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_19/src ] ; then
  echo release CMSSW_10_6_19 already exists
else
  scram p CMSSW CMSSW_10_6_19
fi
cd CMSSW_10_6_19/src
eval `scram runtime -sh`
scram b
cd ../../
SEED=$(date +%s)

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;



#cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) --python_filename LHE-GEN-SIM_cfg.py --eventcontent RAWSIM,LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --fileout file:LHE-GEN-SIM.root --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})"\\nprocess.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)" --step LHE,GEN,SIM --geometry DB:Extended --era Run2_2017 --no_exec --mc -n $NEVENTS || exit $? ;
cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--python_filename LHE-GEN_cfg.py \
--eventcontent RAWSIM,LHE \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN,LHE \
--fileout file:LHE-GEN.root \
--conditions 106X_mc2017_realistic_v6 \
--beamspot Realistic25ns13TeVEarly2017Collision \
--step LHE,GEN \
--geometry DB:Extended \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;



cmsRun LHE-GEN_cfg.py | tee LHE-GEN_log.txt

echo "Files in dir are"
ls
# --------------------------------------------PREMIX data------------------------------------------------------
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd ../../

# cmsDriver.py  --python_filename SIM_cfg.py \
# --filein file:LHE-GEN.root \
# --fileout file:SIM.root \
# --eventcontent RAWSIM \
# --customise Configuration/DataProcessing/Utils.addMonitoring \
# --datatier GEN-SIM \
# --conditions 106X_mc2017_realistic_v6 \
# --beamspot Realistic25ns13TeVEarly2017Collision \
# --step SIM \
# --geometry DB:Extended \
# --era Run2_2017 \
# --runUnscheduled \
# --no_exec \
# --mc \
# -n $NEVENTS || exit $? ;

# cmsRun SIM_cfg.py | tee SIM_log.txt

cmsDriver.py  --python_filename PREMIX_cfg.py \
--filein file:LHE-GEN.root \
--fileout file:PREMIX.root \
--step SIM,DIGI,DATAMIX,L1,DIGI2RAW \
--eventcontent PREMIXRAW \
--conditions 106X_mc2017_realistic_v6 \
--runUnscheduled \
--beamspot Realistic25ns13TeVEarly2017Collision \
--customise_commands 'process.PREMIXRAWoutput.outputCommands.append("drop *_g4SimHits_*_*")' \
--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX" \
--procModifiers premix_stage2 \
--datamix PreMix \
--geometry DB:Extended \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun PREMIX_cfg.py | tee PREMIX_log.txt

# # --------------------------------------------PREMIX+HLT data------------------------------------------------------
if [ -r CMSSW_9_4_14_UL_patch1/src ] ; then
  echo release CMSSW_9_4_14_UL_patch1 already exists
else
  scram p CMSSW CMSSW_9_4_14_UL_patch1
fi
cd CMSSW_9_4_14_UL_patch1/src
eval `scram runtime -sh`
scram b
cd ../../

cmsDriver.py  --python_filename HLT_cfg.py \
--filein file:PREMIX.root \
--fileout file:HLT.root \
--eventcontent RAWSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM-RAW \
--conditions 94X_mc2017_realistic_v15 \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--step HLT:2e34v40 \
--geometry DB:Extended \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun HLT_cfg.py | tee HLT_log.txt

# # --------------------------------------------AOD------------------------------------------------------
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd ../../

cmsDriver.py  --python_filename AOD_cfg.py \
--filein file:HLT.root \
--fileout file:AOD.root \
--eventcontent AODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier AODSIM \
--conditions 106X_mc2017_realistic_v6 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM \
--geometry DB:Extended \
--era Run2_2017 \
--runUnscheduled \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun AOD_cfg.py | tee AOD_log.txt

# # --------------------------------------------miniAOD------------------------------------------------------
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_20 already exists
else
  scram p CMSSW CMSSW_10_6_20
fi
cd CMSSW_10_6_20/src
eval `scram runtime -sh`
scram b
cd ../../

cmsDriver.py  --python_filename miniAOD_cfg.py \
--filein file:AOD.root \
--fileout file:miniAOD.root \
--eventcontent MINIAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier MINIAODSIM \
--fileout file:miniAOD.root \
--conditions 106X_mc2017_realistic_v9 \
--step PAT \
--procModifiers run2_miniAOD_UL \
--geometry DB:Extended \
--era Run2_2017 \
--runUnscheduled \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun miniAOD_cfg.py | tee miniAOD_log.txt

# # --------------------------------------------nanoAOD------------------------------------------------------
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`
scram b
cd ../../

cmsDriver.py  --python_filename nanoAOD_cfg.py \
--filein file:miniAOD.root \
--fileout file:nanoAOD.root \
--eventcontent NANOEDMAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier NANOAODSIM \
--conditions 106X_mc2017_realistic_v9 \
--step NANO \
--era Run2_2017,run2_nanoAOD_106Xv2 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun nanoAOD_cfg.py | tee nanoAOD_log.txt


end=`date +%s`

runtime=$((end-start))
echo "Number of seconds to run = " $runtime