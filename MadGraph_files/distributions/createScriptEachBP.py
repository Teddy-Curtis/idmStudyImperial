import os

# The aim of this is to write a SINGLE script that runs the distributions at different BPs
# but this will all be saved in one single folder rather than many different ones.

definitions = ['define l- = e- mu-', 'define l+ = e+ mu+', 'define vl = ve vm vt', 'define vl~ = ve~ vm~ vt~']

process = 'p p > h2 h2 l+ l- vl vl~'

process_name = 'h2h2lPlMvv_lem_vemt'
output_dir = f'/vols/cms/emc21/idmStudy/MadGraph_files/distributions/{process_name}'

# Make the directory 
try :
    os.mkdir(output_dir)
except:
    print('Directory already made.')


# Params in the form: MH, MA, MHPM, Lam2, Lam345, wh3, whP with wX being the width of the particle
BP_params = [[72.77, 107.803, 114.639, 1.44513, -0.00440723, 3.26701e-05, 9.95367624415e-05], 
            [65, 71.525, 112.85, 0.779115, 0.0004, 8.33387e-09, 0.00027545884846], 
            [67.07, 73.222, 96.73, 0, 0.00738, 6.24072e-09, 2.4286409257e-05], 
            [73.68, 100.112, 145.728, 2.08602, -0.00440723, 8.49308e-06, 0.00217563111117], 
            [72.14, 109.548, 154.761, 0.0125664, -0.00234, 4.46479e-05, 0.0121323319543], 
            [76.55, 134.563, 174.367, 1.94779, 0.0044, 0.000400455, 0.141594920929], 
            [70.91, 148.664, 175.89, 0.439823, 0.0058, 0.001975233, 0.227840304005], 
            [56.78, 166.22, 178.24, 0.502655, 0.00338, 0.1325744, 0.451325051057], 
            [76.69, 154.579, 163.045, 3.92071, 0.0096, 0.002093602, 0.0321421071341], 
            [98.88, 155.037, 155.438, 1.18124, -0.0628, 0.000384, 0.000539004332907], 
            [58.31, 171.148, 172.96, 0.540354, 0.00762, 0.1759649, 0.338925632214], 
            [99.65, 138.484, 181.321, 2.46301, 0.0532, 6.10555e-05, 0.011074980481], 
            [71.03, 165.604, 175.971, 0.339292, 0.00596, 0.01995929, 0.227607240774],
            [71.03, 217.656, 218.738, 0.766549, 0.00214, 0.943497, 1.2280414333], 
            [71.33, 203.796, 229.092, 1.03044, -0.00122, 0.575598, 1.58187675876], 
            [147, 194.647, 197.403, 0.387, -0.018, 0.0001938375, 0.000340806562186], 
            [165.8, 190.082, 195.999, 2.7675, -0.004, 6.93293e-06, 2.60688148477e-05], 
            [191.8, 198.376, 199.721, 1.5075, 0.008, 9.49168e-09, 3.39333286174e-08], 
            [57.475, 288.031, 299.536, 0.929911, 0.00192, 4.59356657115, 5.8717226777], 
            [71.42, 247.224, 258.382, 1.04301, -0.0032, 1.99823799619, 2.8642450432],
            [62.69, 162.397, 190.822, 2.63894, 0.0056, 0.0489534, 0.622261554879]]



for i in range(len(BP_params)):
    BP = f'BP{i+1}'
    params = BP_params[i]
    output_folder = f'{output_dir}/{BP}'

    try :
        os.mkdir(output_folder)
    except:
        print(f'Output folder for {BP} already made.')


    with open(f'{output_folder}/run_script.sh', 'w') as f:
        f.write('import model InertDoublet_UFO \n')
        for defintion in definitions:
            f.write(f'{defintion} \n')
        f.write(f'generate {process} \n')
        f.write(f'output {output_folder}/{process_name}_{BP} \n')
            
        f.write(f'launch {output_folder}/{process_name}_{BP} \n')


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
        f.write(f'set param_card DECAY 36 {params[5]} \n')
        f.write(f'set param_card DECAY 37 {params[6]} \n')

    # Finally add this to the file so that it outputs all of the xs for all the runs
    with open(f'{output_folder}/run_script.sh', 'a') as f:
        f.write(f'launch {output_folder}/{process_name}_{BP} -i \n')
        f.write(f'print_results --path={output_folder}/{process_name}_{BP}/cross_section.txt --format=short \n')