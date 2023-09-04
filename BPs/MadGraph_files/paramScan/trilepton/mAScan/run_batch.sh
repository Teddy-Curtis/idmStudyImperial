ulimit -s unlimited
source ~/.bashrc
cd //vols/cms/emc21/idmStudy/BPs/MG5_aMC_v2_6_7/

BP=$1
split=$2
dir=/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/trilepton/mAScan
run_name=h2h2lllnu

./bin/mg5_aMC ${dir}/${run_name}/MG_script_BP${BP}_mA_split_${split}.sh

mv ${dir}/run_batch.sh.e${JOB_ID} ${dir}/${run_name}/${run_name}_BP${BP}_mA_split_${split}/.
mv ${dir}/run_batch.sh.o${JOB_ID} ${dir}/${run_name}/${run_name}_BP${BP}_mA_split_${split}/.
# command line script to run:
# for BP in 2 5 6; do for split in 10 20 30; do qsub -q hep.q -cwd -l h_rt=36:0:0 -pe hep.pe 4 run_batch.sh ${BP} ${split}; done; done