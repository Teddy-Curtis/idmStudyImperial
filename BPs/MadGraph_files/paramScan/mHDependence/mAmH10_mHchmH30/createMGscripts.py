import os
import random

# The aim of this is to write a SINGLE script that runs the distributions at different BPs
# but this will all be saved in one single folder rather than many different ones.

definitions = ['define l- = e- mu-', 'define l+ = e+ mu+', 'define vl = ve vm vt', 'define vl~ = ve~ vm~ vt~']
#definitions = ['define l = e- mu- e+ mu+', 'define vl = ve vm vt ve~ vm~ vt~']

#process = 'p p > h2 h2 l l l vl'
process = 'p p > h2 h2 l+ l- vl vl~'

process_name = 'h2h2lPlMnunu'
output_dir = f'/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/mHDependence/mAmH10_mHchmH30/{process_name}'

# Make the directory 
try :
    os.mkdir(output_dir)
except:
    print('Directory already made.')


# Params in the form: MH, MA, MHPM, Lam2, Lam345, wh3, whP with wX being the width of the particle
BP_params = {"BP22" : [80, 90, 110, 0, 0.0001],
             "BP24" : [100, 110, 130, 0, 0.0001],
             "BP25" : [140, 150, 170, 0, 0.0001],
             "BP26" : [180, 190, 210, 0, 0.0001],
             "BP27" : [220, 230, 250, 0, 0.0001]}



for BP, params in BP_params.items():
    print(f"BP = {BP}")
    mH = params[0]

    with open(f'{output_dir}/MG_script_mH_{mH}.sh', 'w') as f:
        f.write('import model InertDoublet_UFO \n')
        for defintion in definitions:
            f.write(f'{defintion} \n')
        f.write(f'generate {process} \n')
        f.write(f'output {output_dir}/{process_name}_mH_{mH} \n')
            
        f.write(f'launch {output_dir}/{process_name}_mH_{mH} \n')


        # Set the SM constants according to the PDG
        f.write(f'set param_card frblock 1 {7.297353e-03} \n')
        f.write(f'set param_card frblock 2 {1.166379e-05} \n')


        # Set the masses 
        # Have the manually set the higgs mass (as it is auto at 1)
        # and they use a W mass of ~79 for some reason... so set that too
        f.write(f'set param_card frblock 4 {8.0377e+01} \n')
        f.write(f'set param_card frblock 12 {125.25} \n')
        f.write(f'set param_card frblock 13 {params[0]} \n')
        f.write(f'set param_card frblock 14 {params[1]} \n')
        f.write(f'set param_card frblock 15 {params[2]} \n')
        
        f.write(f'set param_card mass 24 {8.0377e+01} \n')
        f.write(f'set param_card mass 25 {125.25} \n')
        f.write(f'set param_card mass 35 {params[0]} \n')
        f.write(f'set param_card mass 36 {params[1]} \n')
        f.write(f'set param_card mass 37 {params[2]} \n')
        


        # set param_card the coupling constants
        f.write(f'set param_card frblock 11 {params[3]/2} \n')
        f.write(f'set param_card frblock 10 {params[4]/2} \n')

        # set param_card the widths
        f.write(f'set param_card DECAY 6 auto \n')
        f.write(f'set param_card DECAY 23 auto \n')
        f.write(f'set param_card DECAY 24 auto \n')
        f.write(f'set param_card DECAY 25 auto \n')
        f.write(f'set param_card DECAY 36 auto \n')
        f.write(f'set param_card DECAY 37 auto \n')
        
        # Run card settings
        f.write(f'set ptl 1 \n')
        f.write(f'set nevents 10000 \n')
        f.write(f'set iseed {random.randint(0,10000)} \n')


        f.write(f'launch {output_dir}/{process_name}_mH_{mH} -i \n')
        f.write(f'print_results --path={output_dir}/{process_name}_mH_{mH}/cross_section.txt --format=short \n')
