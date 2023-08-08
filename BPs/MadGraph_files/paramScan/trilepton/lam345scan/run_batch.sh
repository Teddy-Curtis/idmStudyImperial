ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

BP=$1
lam=$2
dir=/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/trilepton/lam345scan
run_name=h2h2lllnu

./bin/mg5_aMC ${dir}/${run_name}/MG_script_BP${BP}_lam345_${lam}.sh

mv ${dir}/run_batch.sh.e${JOB_ID} ${dir}/${run_name}/${run_name}_BP${BP}_lam345_${lam}/.
mv ${dir}/run_batch.sh.o${JOB_ID} ${dir}/${run_name}/${run_name}_BP${BP}_lam345_${lam}/.
# command line script to run:
# for BP in 2 5 6; do for lam in -1 0 1 2; do qsub -q hep.q -cwd -l h_rt=36:0:0 -pe hep.pe 4 run_batch.sh ${BP} ${lam}; done; done