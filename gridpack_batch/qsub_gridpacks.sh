#!/bin/bash
#$-q hep.q -l h_rt=4:0:0 -cwd
ulimit -s unlimited
source ~/.bashrc
cd /vols/cms/emc21/idmStudy/genproductions/bin/MadGraph5_aMCatNLO

./gridpack_generation.sh h2h2lPlM_lem_BP1 cards/iDM/h2h2lPlM_lem/h2h2lPlM_lem_BP1

