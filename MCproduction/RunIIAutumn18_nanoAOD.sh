#!/bin/bash
start=`date +%s`

# IF YOU'RE RUNNING LOCALLY THEN COMMENT THIS SEED LINE OUT AND PUT A RANDOM NUMBER FOR THE SEED!
SEED=${JOB_ID}
echo "The seed for this job is: " ${SEED}

if (( "$#" != "5" ))
    then
    echo $# $*
    echo "Input parameter needed: <gridpack> <fragment> <nevts> <nthreads> <outpath>"
    echo "./RunIIAutumn18_nanoAOD.sh "
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
--conditions 106X_upgrade2018_realistic_v4 \
--beamspot Realistic25ns13TeVEarly2018Collision \
--step LHE,GEN \
--geometry DB:Extended \
--era Run2_2018 \
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
--conditions 106X_upgrade2018_realistic_v11_L1v1 \
--runUnscheduled \
--beamspot Realistic25ns13TeVEarly2018Collision \
--customise_commands 'process.PREMIXRAWoutput.outputCommands.append("drop *_g4SimHits_*_*")' \
--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX" \
--procModifiers premix_stage2 \
--datamix PreMix \
--geometry DB:Extended \
--era Run2_2018 \
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
if [ -r CMSSW_10_2_16_UL/src ] ; then
  echo release CMSSW_10_2_16_UL already exists
else
  scram p CMSSW CMSSW_10_2_16_UL
fi
cd CMSSW_10_2_16_UL/src
eval `scram runtime -sh`
scram b
cd $OUTPATH

cmsDriver.py  --python_filename HLT_cfg_${SEED}.py \
--filein file:PREMIX_${SEED}.root \
--fileout file:HLT_${SEED}.root \
--eventcontent RAWSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM-RAW \
--conditions 102X_upgrade2018_realistic_v15 \
--customise_commands 'process.source.bypassVersionCheck = cms.untracked.bool(True)' \
--step HLT:2018v32 \
--geometry DB:Extended \
--era Run2_2018 \
--no_exec \
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
--conditions 106X_upgrade2018_realistic_v11_L1v1 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM \
--geometry DB:Extended \
--era Run2_2018 \
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
if [ -r CMSSW_10_6_20/src ] ; then
  echo release CMSSW_10_6_20 already exists
else
  scram p CMSSW CMSSW_10_6_20
fi
cd CMSSW_10_6_20/src
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
--conditions 106X_upgrade2018_realistic_v16_L1v1 \
--step PAT \
--procModifiers run2_miniAOD_UL \
--geometry DB:Extended \
--era Run2_2018 \
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
--conditions 106X_upgrade2018_realistic_v16_L1v1 \
--step NANO \
--era Run2_2018,run2_nanoAOD_106Xv2 \
--no_exec \
--nThreads ${NTHREADS} \
--mc \
-n $NEVENTS || exit $? ;

cmsRun nanoAOD_cfg_${SEED}.py 


# Move the log and error files over to the directory, as well as a copy of the shell script used to make it 
mkdir -p Autumn18Data
mv miniAOD_${SEED}.root Autumn18Data/.
mv nanoAOD_${SEED}.root Autumn18Data/.
mv /vols/cms/emc21/idmStudy/MCproduction/logging/qsub_2018_nanoAODproduction.sh.e${JOB_ID} Autumn18Data/.
mv /vols/cms/emc21/idmStudy/MCproduction/logging/qsub_2018_nanoAODproduction.sh.o${JOB_ID} Autumn18Data/.
mv LHE-GEN_cfg_${JOB_ID}.py Autumn18Data/.
mv PREMIX_cfg_${JOB_ID}.py Autumn18Data/.
mv HLT_cfg_${JOB_ID}.py Autumn18Data/.
mv AOD_cfg_${JOB_ID}.py Autumn18Data/.
mv miniAOD_cfg_${JOB_ID}.py Autumn18Data/.
mv nanoAOD_cfg_${JOB_ID}.py Autumn18Data/.

end=`date +%s`

runtime=$((end-start))
echo "Number of seconds to run = " $runtime