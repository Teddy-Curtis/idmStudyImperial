import os


# Params in the form: MH, MA, MHPM, Lam2, Lam345
BP_params = [[72.77, 107.803, 114.639, 1.44513, -0.00440723], 
                      [65, 71.525, 112.85, 0.779115, 0.0004], 
                          [67.07, 73.222, 96.73, 0, 0.00738], 
             [73.68, 100.112, 145.728, 2.08602, -0.00440723], 
              [72.14, 109.548, 154.761, 0.0125664, -0.00234], 
                  [76.55, 134.563, 174.367, 1.94779, 0.0044], 
                  [70.91, 148.664, 175.89, 0.439823, 0.0058], 
                    [56.78, 166.22, 178.24, 0.502655, 0.00338], 
                  [76.69, 154.579, 163.045, 3.92071, 0.0096],
                   [58.31, 171.148, 172.96, 0.540354, 0.00762], 
                  [99.65, 138.484, 181.321, 2.46301, 0.0532], 
                 [71.03, 165.604, 175.971, 0.339292, 0.00596],
                   [71.03, 217.656, 218.738, 0.766549, 0.00214], 
                   [71.33, 203.796, 229.092, 1.03044, -0.00122], 
                     [147, 194.647, 197.403, 0.387, -0.018], 
                   [165.8, 190.082, 195.999, 2.7675, -0.004], 
                    [191.8, 198.376, 199.721, 1.5075, 0.008], 
             [57.475, 288.031, 299.536, 0.929911, 0.00192], 
               [71.42, 247.224, 258.382, 1.04301, -0.0032],
                    [62.69, 162.397, 190.822, 2.63894, 0.0056]]


for BP_num, params in enumerate(BP_params):
    filedata = None
    with open('BP_template.dat', 'r') as f:
        filedata = f.read()

    # Replace the target string
    filedata = filedata.replace('$MH0', str(params[0]))
    filedata = filedata.replace('$MA0', str(params[1]))
    filedata = filedata.replace('$MHCH', str(params[2]))
    filedata = filedata.replace('$LAM2', str(params[3]/2))
    filedata = filedata.replace('$LAML', str(params[4]/2))

    # Write the file out again
    with open(f'BPs/BP_paramcard_format/BP{BP_num+1}.dat', 'w') as f:
        f.write(filedata)


    # Now do the same but for the set format template
    filedata = None
    with open('BP_set_template.dat', 'r') as f:
        filedata = f.read()
    # Replace the target string
    filedata = filedata.replace('$MH0', str(params[0]))
    filedata = filedata.replace('$MA0', str(params[1]))
    filedata = filedata.replace('$MHCH', str(params[2]))
    filedata = filedata.replace('$LAM2', str(params[3]/2))
    filedata = filedata.replace('$LAML', str(params[4]/2))
    # Write the file out again
    with open(f'BPs/BP_set_format/BP{BP_num+1}.dat', 'w') as f:
        f.write(filedata)