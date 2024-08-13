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
xrdcp /afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/PU_lists/pulist_2022.txt .

GRIDPACK="${WORKING_DIR}/$(basename -- $GRIDPACK)"
FRAGMENT="${WORKING_DIR}/$(basename -- $FRAGMENT)"
echo "ls"
ls


SCRAM_ARCH=el8_amd64_gcc10; export SCRAM_ARCH
scram arch


#export X509_USER_PROXY=cms.proxy

# This runs differently on lx02 batch than it does on condor. On condor it 
# runs on a separate machine so when it creates a CMSSW env it is on that machine
# and it goes when the program stops. Whereas on lx02, it runs in the directory 
# so the CMSSW folder: 1. doesn't go, 2. If I run multiple qsub at a time then 
# they all use the same folders and it breaks.


# --------------------------------------------LHE, GEN------------------------------------------------------
# For this first step, as I need to save the fragment WITHIN CMSSW_12_4_11_patch3, then build it,
# I will have a CMSSW_12_4_11_patch3 for each BP, but will delete it after I use it to save space 
source /cvmfs/cms.cern.ch/cmsset_default.sh

cmsrel CMSSW_12_4_11_patch3
cd CMSSW_12_4_11_patch3/src
eval `scram runtime -sh`

mkdir -p Configuration/GenProduction/python/
cp ${FRAGMENT}  Configuration/GenProduction/python/
# This goes into the fragment, and changes all occurances of @GRIDPACK with 
# the location of the correct gridpack
sed -i "s!@GRIDPACK!${GRIDPACK}!" Configuration/GenProduction/python/$(basename $FRAGMENT)

[ -s Configuration/GenProduction/python/$(basename $FRAGMENT) ] || exit $?;

scram b
cd $WORKING_DIR

# # # # cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
# # # # --python_filename LHE-GEN_cfg_${SEED}.py \
# # # # --eventcontent RAWSIM,LHE \
# # # # --customise Configuration/DataProcessing/Utils.addMonitoring \
# # # # --datatier GEN,LHE \
# # # # --fileout file:LHE-GEN_${SEED}.root \
# # # # --conditions 106X_upgrade2018_realistic_v4 \
# # # # --beamspot Realistic25ns13TeVEarly2018Collision \
# # # # --step LHE,GEN \
# # # # --geometry DB:Extended \
# # # # --era Run2_2018 \
# # # # --no_exec \
# # # # --mc \
# # # # --customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" \
# # # # -n $NEVENTS || exit $? ;


#! Potentially change the GEN-SIM,LHE to just GEN, LHE like before
cmsDriver.py Configuration/GenProduction/python/$(basename $FRAGMENT) \
--python_filename LHE-GEN_cfg_${SEED}.py \
--eventcontent RAWSIM,LHE \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM,LHE \
--fileout file:LHE-GEN_${SEED}.root \
--conditions 124X_mcRun3_2022_realistic_v12 \
--beamspot Realistic25ns13p6TeVEarly2022Collision \
--customise_commands process.RandomNumberGeneratorService.externalLHEProducer.initialSeed="int(${SEED})" \
--step LHE,GEN,SIM \
--geometry DB:Extended \
--era Run3 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

echo "########################### 1 RUNNING THE FIRST CMSDRIVER OPTIONS"

cmsRun LHE-GEN_cfg_${SEED}.py 
echo "ls"
ls
# # I can now delete the CMSSW install in this BP, but first I want to copy over the fragment for if I need it later
# cp $FRAGMENT .
# Now delete the CMSSW version
#! Maybe delete if not needed later 
# rm -rf CMSSW_12_4_11_patch3



# --------------------------------------------PREMIX+HLT data------------------------------------------------------
# Make these in the directory above so that I don't need to make a CMSSW for each BP
cd $WORKING_DIR

echo "Choose random PU input file."
PULIST=($(cat pulist_2022.txt))
PUFILE=${PULIST[$RANDOM % ${#PULIST[@]}]}
echo "Chose PU File: ${PUFILE}"

# # # # # # cmsDriver.py  --python_filename PREMIX_cfg_${SEED}.py \
# # # # # # --filein file:LHE-GEN_${SEED}.root \
# # # # # # --fileout file:PREMIX_${SEED}.root \
# # # # # # --step SIM,DIGI,DATAMIX,L1,DIGI2RAW \
# # # # # # --eventcontent PREMIXRAW \
# # # # # # --conditions 106X_upgrade2018_realistic_v11_L1v1 \
# # # # # # --runUnscheduled \
# # # # # # --beamspot Realistic25ns13TeVEarly2018Collision \
# # # # # # --pileup_input "$PUFILE" \
# # # # # # --procModifiers premix_stage2 \
# # # # # # --datamix PreMix \
# # # # # # --geometry DB:Extended \
# # # # # # --era Run2_2018 \
# # # # # # --no_exec \
# # # # # # --mc \
# # # # # # -n $NEVENTS || exit $? ;




cmsDriver.py  --python_filename PREMIX_cfg_${SEED}.py \
--eventcontent PREMIXRAW \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier GEN-SIM-RAW \
--fileout file:HLT_${SEED}.root \
--pileup_input "$PUFILE" \
--conditions 124X_mcRun3_2022_realistic_v12 \
--step DIGI,DATAMIX,L1,DIGI2RAW,HLT:2022v12 \
--procModifiers premix_stage2,siPixelQualityRawToDigi \
--geometry DB:Extended \
--filein file:LHE-GEN_${SEED}.root \
--datamix PreMix \
--era Run3 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;


echo "########################### 2 RUNNING THE SECOND CMSDRIVER OPTIONS"

cmsRun PREMIX_cfg_${SEED}.py

echo "ls"
ls

# Now that I've used LHE-GEN I can get rid of that file
rm LHE-GEN_${SEED}.root
rm LHE-GEN_${SEED}_inLHE.root

# # --------------------------------------------AOD------------------------------------------------------

# cmsDriver command
cmsDriver.py  --python_filename AOD_cfg_${SEED}.py \
--eventcontent AODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier AODSIM \
--fileout file:AOD_${SEED}.root \
--conditions 124X_mcRun3_2022_realistic_v12 \
--step RAW2DIGI,L1Reco,RECO,RECOSIM \
--procModifiers siPixelQualityRawToDigi \
--geometry DB:Extended \
--filein file:HLT_${SEED}.root \
--era Run3 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

echo "########################### 3 RUNNING THE THIRD CMSDRIVER OPTIONS"

cmsRun AOD_cfg_${SEED}.py 

echo "ls"
ls

# Now that I've used HLT I can get rid of that file
rm HLT_${SEED}.root

# # --------------------------------------------miniAOD------------------------------------------------------

SCRAM_ARCH=el8_amd64_gcc11; export SCRAM_ARCH
scram arch

cmsrel CMSSW_13_0_13
cd CMSSW_13_0_13/src
eval `scram runtime -sh`
scram b
cd $WORKING_DIR

# # # # # # # cmsDriver.py  --python_filename miniAOD_cfg_${SEED}.py \
# # # # # # # --filein file:AOD_${SEED}.root \
# # # # # # # --fileout file:miniAOD_${SEED}.root \
# # # # # # # --eventcontent MINIAODSIM \
# # # # # # # --customise Configuration/DataProcessing/Utils.addMonitoring \
# # # # # # # --datatier MINIAODSIM \
# # # # # # # --fileout file:miniAOD_${SEED}.root \
# # # # # # # --conditions 106X_upgrade2018_realistic_v16_L1v1 \
# # # # # # # --step PAT \
# # # # # # # --procModifiers run2_miniAOD_UL \
# # # # # # # --geometry DB:Extended \
# # # # # # # --era Run2_2018 \
# # # # # # # --runUnscheduled \
# # # # # # # --no_exec \
# # # # # # # --mc \
# # # # # # # -n $NEVENTS || exit $? ;



cmsDriver.py  --python_filename miniAOD_cfg_${SEED}.py \
--eventcontent MINIAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier MINIAODSIM \
--fileout file:miniAOD_${SEED}.root \
--conditions 130X_mcRun3_2022_realistic_v5 \
--step PAT \
--geometry DB:Extended \
--filein file:AOD_${SEED}.root \
--era Run3,run3_miniAOD_12X \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

echo "########################### 4 RUNNING THE FOURTH CMSDRIVER OPTIONS"

cmsRun miniAOD_cfg_${SEED}.py 

echo "ls"
ls

# Now that I've used AOD I can get rid of that file
rm AOD_${SEED}.root
#! Maybe delete if not needed 
# rm -rf CMSSW_10_6_20

# # --------------------------------------------nanoAOD------------------------------------------------------

cd $WORKING_DIR

cmsDriver.py  --python_filename nanoAOD_cfg_${SEED}.py \
--eventcontent NANOAODSIM \
--customise Configuration/DataProcessing/Utils.addMonitoring \
--datatier NANOAODSIM \
--fileout file:nanoAOD_${SEED}.root \
--conditions 130X_mcRun3_2022_realistic_v5 \
--step NANO \
--scenario pp \
--filein file:miniAOD_${SEED}.root \
--era Run3 \
--no_exec \
--mc \
-n $NEVENTS || exit $? ;

echo "########################### 5 RUNNING THE FIFTH CMSDRIVER OPTIONS"

cmsRun nanoAOD_cfg_${SEED}.py 

echo "ls"
ls

# Copy files over
mkdir -p ${OUTPATH}/Data/Autumn2018Data
xrdcp nanoAOD_${SEED}.root ${OUTPATH}/Data/Autumn2018Data/${run_name}_Autumn2018Data_nanoAOD_${SEED}.root


end=`date +%s`

runtime=$((end-start))
echo "Number of seconds to run = " $runtime