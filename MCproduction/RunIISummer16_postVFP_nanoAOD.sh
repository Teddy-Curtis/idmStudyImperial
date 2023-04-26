#!/bin/bash
start=`date +%s`

SEED=${JOB_ID}
echo "The seed for this job is: " ${SEED}

if (( "$#" != "5" ))
    then
    echo $# $*
    echo "Input parameter needed: <gridpack> <fragment> <nevts> <nthreads> <outpath>"
    echo "./RunIIFall17_nanoAOD.sh "
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
if [ "${CURRENT_DIR:0:5}" = "/vols" ]; then
    echo "On Imperial servers therefore changing the batch directory to $OUTPATH"
    cd $OUTPATH
else
    echo "Running on CERN servers, therefore not changing directory from the condor machine"
fi

# --------------------------------------------LHE, GEN------------------------------------------------------
#!/bin/bash
# For this first step, as I need to save the fragment WITHIN CMSSW_10_6_18, then build it,
# I will have a CMSSW_10_6_18 for each BP, but will delete it after I use it to save space 
source /cvmfs/cms.cern.ch/cmsset_default.sh
if [ -r CMSSW_10_6_18/src ] ; then
  echo release CMSSW_10_6_18 already exists
else
  scram p CMSSW CMSSW_10_6_18
fi
cd CMSSW_10_6_18/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
# This goes into the fragment, and changes all occurances of @GRIDPACK with 
# the location of the correct gridpack
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd ../../


cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--python_filename LHE-GEN_cfg_${SEED}.py \
--eventcontent RAWSIM,LHE \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN,LHE \
--fileout file:LHE-GEN_${SEED}.root \
--conditions 106X_mcRun2_asymptotic_v13 \
--beamspot Realistic25ns13TeV2016Collision \
--step LHE,GEN \
--geometry DB:Extended \
--era Run2_2016 \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
--customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" \
-n $NEVENTS || exit $? ;

cmsRun LHE-GEN_cfg_${SEED}.py 

# I can now delete the CMSSW install in this BP, but first I want to copy over the fragment for if I need it later
cp $FRAGMENT .
# Now delete the CMSSW version
#rm -rf CMSSW_10_6_18

# --------------------------------------------PREMIX data------------------------------------------------------
# Make these in the directory above so that I don't need to make a CMSSW for each BP
cd ..
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename PREMIX_cfg_${SEED}.py \
--filein file:LHE-GEN_${SEED}.root \
--fileout file:PREMIX_${SEED}.root \
--step SIM,DIGI,DATAMIX,L1,DIGI2RAW \
--eventcontent PREMIXRAW \
--conditions 106X_mcRun2_asymptotic_v13 \
--runUnscheduled \
--beamspot Realistic25ns13TeV2016Collision \
--customise_commands 'process.PREMIXRAWoutput.outputCommands.append("drop *_g4SimHits_*_*")' \
--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX" \
--procModifiers premix_stage2 \
--datamix PreMix \
--geometry DB:Extended \
--era Run2_2016 \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun PREMIX_cfg_${SEED}.py

# Now that I've used LHE-GEN I can get rid of that file
rm LHE-GEN_${SEED}.root
rm LHE-GEN_${SEED}_inLHE.root

# # --------------------------------------------PREMIX+HLT data------------------------------------------------------
cd ..
if [ -r CMSSW_8_0_33_UL/src ] ; then
  echo release CMSSW_8_0_33_UL already exists
else
  scram p CMSSW CMSSW_8_0_33_UL
fi
cd CMSSW_8_0_33_UL/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename HLT_cfg_${SEED}.py \
--filein file:PREMIX_${SEED}.root \
--fileout file:HLT_${SEED}.root \
--eventcontent RAWSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM-RAW \
--conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6  \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--step HLT:25ns15e33_v4 \
--geometry DB:Extended \
--era Run2_2016 \
--no_exec \
--outputCommand "keep *_mix_*_*,keep *_genPUProtons_*_*" \
--inputCommands "keep *","drop *_*_BMTF_*","drop *PixelFEDChannel*_*_*_*" \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun HLT_cfg_${SEED}.py 

# Now that I've used PREMIX I can get rid of that file
rm PREMIX_${SEED}.root

# # --------------------------------------------AOD------------------------------------------------------
cd ..
if [ -r CMSSW_10_6_17_patch1/src ] ; then
  echo release CMSSW_10_6_17_patch1 already exists
else
  scram p CMSSW CMSSW_10_6_17_patch1
fi
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename AOD_cfg_${SEED}.py \
--filein file:HLT_${SEED}.root \
--fileout file:AOD_${SEED}.root \
--eventcontent AODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier AODSIM \
--conditions 106X_mcRun2_asymptotic_v13 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM \
--geometry DB:Extended \
--era Run2_2016 \
--runUnscheduled \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun AOD_cfg_${SEED}.py 

# Now that I've used HLT I can get rid of that file
rm HLT_${SEED}.root

# # --------------------------------------------miniAOD------------------------------------------------------
cd ..
if [ -r CMSSW_10_6_25/src ] ; then
  echo release CMSSW_10_6_25 already exists
else
  scram p CMSSW CMSSW_10_6_25
fi
cd CMSSW_10_6_25/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename miniAOD_cfg_${SEED}.py \
--filein file:AOD_${SEED}.root \
--fileout file:miniAOD_${SEED}.root \
--eventcontent MINIAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier MINIAODSIM \
--fileout file:miniAOD_${SEED}.root \
--conditions 106X_mcRun2_asymptotic_v17 \
--step PAT \
--procModifiers run2_miniAOD_UL \
--geometry DB:Extended \
--era Run2_2016 \
--runUnscheduled \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun miniAOD_cfg_${SEED}.py 

# Now that I've used AOD I can get rid of that file
rm AOD_${SEED}.root

# # --------------------------------------------nanoAOD------------------------------------------------------
cd ..
if [ -r CMSSW_10_6_26/src ] ; then
  echo release CMSSW_10_6_26 already exists
else
  scram p CMSSW CMSSW_10_6_26
fi
cd CMSSW_10_6_26/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename nanoAOD_cfg_${SEED}.py \
--filein file:miniAOD_${SEED}.root \
--fileout file:nanoAOD_${SEED}.root \
--eventcontent NANOAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier NANOAODSIM \
--conditions 106X_mcRun2_asymptotic_v17 \
--step NANO \
--era Run2_2016,run2_nanoAOD_106Xv2 \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun nanoAOD_cfg_${SEED}.py 


# Move the log and error files over to the directory, as well as a copy of the shell script used to make it 
mkdir -p Summer16Data_postVFP
mv miniAOD_${SEED}.root Summer16Data_postVFP/.
mv nanoAOD_${SEED}.root Summer16Data_postVFP/.
mv /vols/cms/emc21/idmStudy/MCproduction/logging/qsub_2016postVFP_nanoAODproduction.sh.e${JOB_ID} Summer16Data_postVFP/.
mv /vols/cms/emc21/idmStudy/MCproduction/logging/qsub_2016postVFP_nanoAODproduction.sh.o${JOB_ID} Summer16Data_postVFP/.
mv LHE-GEN_cfg_${JOB_ID}.py Summer16Data_postVFP/.
mv PREMIX_cfg_${JOB_ID}.py Summer16Data_postVFP/.
mv HLT_cfg_${JOB_ID}.py Summer16Data_postVFP/.
mv AOD_cfg_${JOB_ID}.py Summer16Data_postVFP/.
mv miniAOD_cfg_${JOB_ID}.py Summer16Data_postVFP/.
mv nanoAOD_cfg_${JOB_ID}.py Summer16Data_postVFP/.

end=`date +%s`

runtime=$((end-start))
echo "Number of seconds to run = " $runtime