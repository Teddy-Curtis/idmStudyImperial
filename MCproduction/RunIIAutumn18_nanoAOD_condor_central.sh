#!/bin/bash
start=`date +%s`

if (( "$#" != "6" ))
    then
    echo $# $*
    echo "Input parameter needed: <proxy> <gridpack> <fragment> <nevts> <outpath>"
    echo "./RunIIAutumn18_nanoAOD.sh "
    exit
fi

i=1
PROXY=${!i}; i=$((i+1))
GRIDPACK=${!i}; i=$((i+1))
FRAGMENT=${!i}; i=$((i+1))
NEVENTS=${!i}; i=$((i+1))
OUTPATH=${!i}; i=$((i+1))
run_name=${!i}; i=$((i+1))


SEED=$(((RANDOM<<15)|RANDOM))
echo "The seed for this job is: " ${SEED}

export HOME=`pwd`
export X509_USER_PROXY=$1
voms-proxy-info -all
voms-proxy-info -all -file $1
WORKING_DIR=`pwd`



xrdcp ${GRIDPACK} .
xrdcp ${FRAGMENT} .
xrdcp /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/PU_lists/pulist_Autumn18.txt .

GRIDPACK="${WORKING_DIR}/$(basename -- $GRIDPACK)"
FRAGMENT="${WORKING_DIR}/$(basename -- $FRAGMENT)"
echo "ls"
ls


SCRAM_ARCH=slc7_amd64_gcc700; export SCRAM_ARCH
scram arch


#export X509_USER_PROXY=cms.proxy

# This runs differently on lx02 batch than it does on condor. On condor it 
# runs on a separate machine so when it creates a CMSSW env it is on that machine
# and it goes when the program stops. Whereas on lx02, it runs in the directory 
# so the CMSSW folder: 1. doesn't go, 2. If I run multiple qsub at a time then 
# they all use the same folders and it breaks.


# --------------------------------------------LHE, GEN------------------------------------------------------
# For this first step, as I need to save the fragment WITHIN CMSSW_10_6_28_patch1, then build it,
# I will have a CMSSW_10_6_28_patch1 for each BP, but will delete it after I use it to save space 
source /cvmfs/cms.cern.ch/cmsset_default.sh

cmsrel CMSSW_10_6_28_patch1
cd CMSSW_10_6_28_patch1/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
# This goes into the fragment, and changes all occurances of @GRIDPACK with 
# the location of the correct gridpack
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd $WORKING_DIR

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
--mc \
--customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" \
-n $NEVENTS || exit $? ;

cmsRun LHE-GEN_cfg_${SEED}.py 
echo "ls"
ls
# # I can now delete the CMSSW install in this BP, but first I want to copy over the fragment for if I need it later
# cp $FRAGMENT .
# Now delete the CMSSW version
rm -rf CMSSW_10_6_28_patch1
# --------------------------------------------PREMIX data------------------------------------------------------
# Make these in the directory above so that I don't need to make a CMSSW for each BP
cd $WORKING_DIR

cmsrel CMSSW_10_6_17_patch1
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd $WORKING_DIR

echo "Choose random PU input file."
PULIST=($(cat pulist_Autumn18.txt))
PUFILE=${PULIST[$RANDOM % ${#PULIST[@]}]}
echo "Chose PU File: ${PUFILE}"

cmsDriver.py  --python_filename PREMIX_cfg_${SEED}.py \
--filein file:LHE-GEN_${SEED}.root \
--fileout file:PREMIX_${SEED}.root \
--step SIM,DIGI,DATAMIX,L1,DIGI2RAW \
--eventcontent PREMIXRAW \
--conditions 106X_upgrade2018_realistic_v11_L1v1 \
--runUnscheduled \
--beamspot Realistic25ns13TeVEarly2018Collision \
--pileup_input "$PUFILE" \
--procModifiers premix_stage2 \
--datamix PreMix \
--geometry DB:Extended \
--era Run2_2018 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

cmsRun PREMIX_cfg_${SEED}.py

# Now that I've used LHE-GEN I can get rid of that file
rm LHE-GEN_${SEED}.root
rm LHE-GEN_${SEED}_inLHE.root
# # --------------------------------------------PREMIX+HLT data------------------------------------------------------

cmsrel CMSSW_10_2_16_UL
cd CMSSW_10_2_16_UL/src
eval `scram runtime -sh`
scram b
cd $WORKING_DIR

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
--mc \
-n $NEVENTS || exit $? ;

cmsRun HLT_cfg_${SEED}.py 

# Now that I've used PREMIX I can get rid of that file
rm PREMIX_${SEED}.root

# # --------------------------------------------AOD------------------------------------------------------
cd $WORKING_DIR
cd CMSSW_10_6_17_patch1/src
eval `scram runtime -sh`
scram b
cd $WORKING_DIR

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
--mc \
-n $NEVENTS || exit $? ;

cmsRun AOD_cfg_${SEED}.py 

# Now that I've used HLT I can get rid of that file
rm HLT_${SEED}.root
rm -rf CMSSW_10_6_17_patch1
# # --------------------------------------------miniAOD------------------------------------------------------


cmsrel CMSSW_10_6_20
cd CMSSW_10_6_20/src
eval `scram runtime -sh`
scram b
cd $WORKING_DIR

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
--mc \
-n $NEVENTS || exit $? ;

cmsRun miniAOD_cfg_${SEED}.py 

# Now that I've used AOD I can get rid of that file
rm AOD_${SEED}.root
rm -rf CMSSW_10_6_20

# # --------------------------------------------nanoAOD------------------------------------------------------

cmsrel CMSSW_10_6_26
cd CMSSW_10_6_26/src
eval `scram runtime -sh`
#scram b
cd $WORKING_DIR


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
--mc \
-n $NEVENTS || exit $? ;

cmsRun nanoAOD_cfg_${SEED}.py 

# Copy files over
mkdir -p ${OUTPATH}/Data/Autumn2018Data
xrdcp nanoAOD_${SEED}.root ${OUTPATH}/Data/Autumn2018Data/${run_name}_Autumn2018Data_nanoAOD_${SEED}.root


end=`date +%s`

runtime=$((end-start))
echo "Number of seconds to run = " $runtime