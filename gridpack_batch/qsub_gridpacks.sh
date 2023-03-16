#!/bin/bash
#$-q hep.q -l h_rt=4:0:0 -cwd
BPNUM=$1
ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/genproductions/bin/MadGraph5_aMCatNLO

./gridpack_generation.sh h2h2lPlM_lem_BP$BPNUM cards/iDM/h2h2lPlM_lem/h2h2lPlM_lem_BP$BPNUM

# for BP in 8 10 12 13 14 18 19 20 21 24; do qsub qsub_gridpacks.sh $BP; done

