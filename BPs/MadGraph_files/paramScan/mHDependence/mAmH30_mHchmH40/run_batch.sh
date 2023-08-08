ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

mH=$1
dir=/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/mHDependence
run_name=h2h2lPlMnunu

./bin/mg5_aMC ${dir}/${run_name}/MG_script_mH_${mH}.sh

mv ${dir}/run_batch.sh.e${JOB_ID} ${dir}/${run_name}/${run_name}_mH_${mH}/.
mv ${dir}/run_batch.sh.o${JOB_ID} ${dir}/${run_name}/${run_name}_mH_${mH}/.
# command line script to run:
# for mH in 60 100 140 180 220; do qsub -q hep.q -cwd -l h_rt=24:0:0 -pe hep.pe 4 run_batch.sh ${mH} ; done