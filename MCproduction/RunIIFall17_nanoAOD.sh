#!/bin/bash


if (( "$#" != "7" ))
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
CMSSW_version=${!i}; i=$((i+1))
scram_version=${!i}; i=$((i+1))

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

# --------------------------------------------LHEGS data------------------------------------------------------
#!/bin/bash
export SCRAM_ARCH=${scram_version}
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r ${CMSSW_version}/src ] ; then
  echo release ${CMSSW_version} already exists
else
  scram p CMSSW ${CMSSW_version}
fi
cd ${CMSSW_version}/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd ../../
SEED=$(date +%s)

#cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) --python_filename LHE-GEN-SIM_cfg.py --eventcontent RAWSIM,LHE --customise Configuration/DataProcessing/Utils.addMonitoring --datatier GEN-SIM,LHE --fileout file:LHE-GEN-SIM.root --conditions 93X_mc2017_realistic_v3 --beamspot Realistic25ns13TeVEarly2017Collision --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})"\\nprocess.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)" --step LHE,GEN,SIM --geometry DB:Extended --era Run2_2017 --no_exec --mc -n $NEVENTS || exit $? ;
cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--python_filename LHE-GEN-SIM_cfg.py \
--eventcontent RAWSIM,LHE \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM,LHE \
--fileout file:LHE-GEN-SIM.root \
--conditions 106X_mc2017_realistic_v6 \
--beamspot Realistic25ns13TeVEarly2017Collision \
--customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})"\\nprocess.source.numberEventsInLuminosityBlock="cms.untracked.uint32(100)" \
--step LHE,GEN,SIM \
--geometry DB:Extended \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun LHE-GEN-SIM_cfg.py | tee LHE-GEN-SIM_log.txt



cmsDriver.py  --python_filename PREMIX_cfg.py \
--filein file:LHE-GEN-SIM.root \
--fileout file:PREMIX.root \
--step DIGI,DATAMIX,L1,DIGI2RAW,HLT:@relval2017 \
--eventcontent PREMIXRAW \
--datatier GEN-SIM-RAW \
--conditions 106X_mc2017_realistic_v6 \
--runUnscheduled \
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

cmsDriver.py --python_filename AOD_cfg.py \
--filein file:PREMIX.root \
--fileout file:AOD.root \
--eventcontent AODSIM \
--datatier AODSIM \
--conditions 106X_mc2017_realistic_v6 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM,EI \
--procModifiers premix_stage2 \
--runUnscheduled \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun AOD_cfg.py | tee AOD_log.txt


cmsDriver.py --python_filename miniAOD_cfg.py \
--filein file:AOD.root \
--fileout file:miniAOD.root \
--eventcontent MINIAODSIM \
--runUnscheduled \
--datatier MINIAODSIM \
--conditions 106X_mc2017_realistic_v6 \
--step PAT \
--geometry DB:Extended \
--era Run2_2017 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun miniAOD_cfg.py | tee miniAOD_log.txt



export SCRAM_ARCH=${scram_version}
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_20 already exists
else
  scram p CMSSW CMSSW_10_6_20
fi
cd CMSSW_10_6_20/src
eval `scram runtime -sh`
scram b
cd ../../
SEED=$(date +%s)


cmsDriver.py  --python_filename nanoAOD_cfg.py /
--eventcontent NANOEDMAODSIM /
--customise Configuration/DataProcessing/Utils.addMonitoring /
--datatier NANOAODSIM /
--fileout file:nanoAOD.root /
--conditions 106X_mc2017_realistic_v9 /
--step NANO /
--filein file:miniAOD.root /
--era Run2_2017,run2_nanoAOD_106Xv2 /
--no_exec /
--mc /
-n $EVENTS || exit $? ;

cmsRun nanoAOD_cfg.py | tee nanoAOD_log.txt