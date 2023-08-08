import os

# The aim of this is to write a SINGLE script that runs the distributions at different BPs
# but this will all be saved in one single folder rather than many different ones.

definitions = ['define l- = e- mu-', 'define l+ = e+ mu+', 'define vl = ve vm vt', 'define vl~ = ve~ vm~ vt~']
#definitions = ['define l = e- mu- e+ mu+', 'define vl = ve vm vt ve~ vm~ vt~']

#process = 'p p > h2 h2 l l l vl'
process = 'p p > h2 h2 l+ l- vl vl~'

process_name = 'h2h2lPlMnunu'
output_dir = f'/vols/cms/emc21/idmStudy/BPs/MadGraph_files/paramScan/BP2_lam345mHch_scan/{process_name}'

# Make the directory 
try :
    os.mkdir(output_dir)
except:
    print('Directory already made.')


# Params in the form: MH, MA, MHPM, Lam2, Lam345, wh3, whP with wX being the width of the particle
BP_params = [65, 71.525, 112.85, 0.779115, 0.0004, 8.33387e-09, 0.00027545884846]
BP="BP2"
mA = BP_params[1]
# I want to loop over different lam345 and different mHch
splits = [1, 40, 80]
lams = [-1, 0, 1, 2]

for split in splits:
    mHch = mA + split
    for lam in lams:
        with open(f'{output_dir}/MG_script_{BP}_mHch_split_{split}_lam345_{lam}.sh', 'w') as f:
            f.write('import model InertDoublet_UFO \n')
            for defintion in definitions:
                f.write(f'{defintion} \n')
            f.write(f'generate {process} \n')
            f.write(f'output {output_dir}/{process_name}_{BP}_mHch_split_{split}_lam345_{lam} \n')
                
            f.write(f'launch {output_dir}/{process_name}_{BP}_mHch_split_{split}_lam345_{lam} \n')


            # Set the SM constants according to the PDG
            f.write(f'set param_card frblock 1 {7.297353e-03} \n')
            f.write(f'set param_card frblock 2 {1.166379e-05} \n')


            # Set the masses 
            # Have the manually set the higgs mass (as it is auto at 1)
            # and they use a W mass of ~79 for some reason... so set that too
            f.write(f'set param_card frblock 4 {8.0377e+01} \n')
            f.write(f'set param_card frblock 12 {125.25} \n')
            f.write(f'set param_card frblock 13 {BP_params[0]} \n')
            f.write(f'set param_card frblock 14 {BP_params[1]} \n')
            f.write(f'set param_card frblock 15 {mHch} \n')
            
            f.write(f'set param_card mass 24 {8.0377e+01} \n')
            f.write(f'set param_card mass 25 {125.25} \n')
            f.write(f'set param_card mass 35 {BP_params[0]} \n')
            f.write(f'set param_card mass 36 {BP_params[1]} \n')
            f.write(f'set param_card mass 37 {mHch} \n')
            


            # set param_card the coupling constants
            f.write(f'set param_card frblock 11 {BP_params[3]/2} \n')
            f.write(f'set param_card frblock 10 {lam/2} \n')

            # set param_card the widths
            f.write(f'set param_card DECAY 6 auto \n')
            f.write(f'set param_card DECAY 23 auto \n')
            f.write(f'set param_card DECAY 24 auto \n')
            f.write(f'set param_card DECAY 25 auto \n')
            f.write(f'set param_card DECAY 36 auto \n')
            f.write(f'set param_card DECAY 37 auto \n')
            
            # Run card settings
            f.write(f'set ptl 1 \n')
            f.write(f'set nevents 20000 \n')


            f.write(f'launch {output_dir}/{process_name}_{BP}_mHch_split_{split}_lam345_{lam} -i \n')
            f.write(f'print_results --path={output_dir}/{process_name}_{BP}_mHch_split_{split}_lam345_{lam}/cross_section.txt --format=short \n')

