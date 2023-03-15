#!/bin/bash
#$-q hep.q -l h_rt=1:00:00 -cwd

# Can submit to batch using 
# "qsub getWidths.sh"

# This is a python file that runs the commandline commands to use madgraph to get the widths
# then save them in the necessary param_card files. 
# I think it will be easier to make a txt file that I input directly
# into madgraph 
base_folder="/vols/cms/emc21/idmStudy/MadGraph_files/BPs_new"

for BP_num in {1..20}
do 
    echo "Finding the A0 width for BP" ${BP_num}
    param_card="${base_folder}/BPs/BP_paramcard_format/BP${BP_num}.dat"
    echo $param_card
    echo "import model InertDoublet_UFO" > process_file.txt
    echo "compute_widths ~A0 --path=${param_card}" >> process_file.txt
    echo "compute_widths ~H+ --path=${param_card}" >> process_file.txt
    # Now put file into madgraph
    /vols/cms/emc21/idmStudy/MG5_aMC_v2_6_7/bin/mg5_aMC ${base_folder}/process_file.txt

done