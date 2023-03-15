#!/bin/bash

cd /afs/cern.ch/user/e/ecurtis/idmStudy/recast/initialComparison
export X509_USER_PROXY=/afs/cern.ch/user/e/ecurtis/cms.proxy
source /afs/cern.ch/user/e/ecurtis/miniconda3/etc/profile.d/conda.sh
conda activate idm
mH=$1
mA=$2

python IDMvs2HDMa.py $mH $mA 