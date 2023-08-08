"""
This is used to show the dependence on lam345 that the distributions 
for the dilepton selections has.
"""

import uproot
import awkward as ak 
import vector
vector.register_awkward()
import matplotlib.pyplot as plt
import os 

# BP_params = {
#     "BP5" : [72.14, 109.548, 154.761, 0.0125664, 0.0, 4.46479e-05, 0.0121323319543],
#     "BP6" : [76.55, 134.563, 174.367, 1.94779, 0.0, 0.000400455, 0.141594920929]}

BP_params = {"BP2" : [65, 71.525, 112.85, 0.779115, 0.0004, 8.33387e-09, 0.00027545884846]}

# This gets the cross-sections of the IDM BPs
def getNumfromString(line):
    l = []
    for t in line.split():
        try:
            l.append(float(t))
        except ValueError:
            pass
    return l[0], l[1]

def getXS(proc, BP, split):
    file = f"{proc}/{proc}_{BP}_mHch_split_{split}//cross_section.txt"
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('run'):
                xs, xs_err = getNumfromString(line)
                return xs




def getVars(part, weights):
    lep = part[(abs(part.PID) == 11) | (abs(part.PID) == 13)]
    lep1, lep2 = lep[:,0], lep[:,1]
    dilep = lep1 + lep2
    cut = lep1['PID'] == -lep2['PID']
    mass = dilep.mass
    mass_cut = mass < 80
    cut = cut & mass_cut
    # lead_pt_cut = lep1.pt >= 10
    # sublead_pt_cut = lep2.pt >= 1
    # pt_cut = lead_pt_cut & sublead_pt_cut
    # cut = cut & pt_cut 
    lep = lep[cut]

    vars = {}
    weights = weights[cut]
    lep1, lep2 = lep[:,0], lep[:,1]
    dilep = lep1 + lep2
    mass = dilep.mass
    vars['mass'] = mass
    dR = lep1.deltaR(lep2)
    vars['dR'] = dR
    leadpt = lep1.pt
    vars['leadpt'] = leadpt

    # Now get the DM particles
    dm = part[part.PID == 35]
    dm = dm[cut]
    # Get vector sum to find the MET 
    dm1 = dm[:,0]
    dm2 = dm[:,1]
    MET = dm1 + dm2
    vars['MET'] = MET.pt
    weights = ak.flatten(weights['Event.Weight'])
    return vars, weights


def appendToDict(vars, my_dict):
    for var, data in vars.items():
        #print(var)
        # Append
        my_dict[var].append(data)
        # Flatten
        #print(my_dict[var][0])
        #my_dict[var] = [itm for lst in my_dict[var] for itm in lst]
    return my_dict

plot_settings = {
    "mass" : {
        "min" : 0,
        "max" : 100,
        "title" : "Dilep Invariant Mass",
        "x" : "Mass (GeV)"
    },
    "dR" : {
        "min" : 0,
        "max" : 4,
        "title" : "dR between dileptons",
        "x" : "dR"
    },
    "leadpt" : {
        "min" : 0,
        "max" : 80,
        "title" : "Lead Lepton PT",
        "x" : "PT (GeV)"
    },
    "MET" : {
        "min" : 0,
        "max" : 150,
        "title" : "MET",
        "x" : "MET (GeV)"
    }
}


def plotDists(BP_params, procs, save_loc):
    variables = {}

    for BP, params in BP_params.items():
        print(f"BP = {BP}")
        mA = params[1]
        mass_splits = [1, 40, 80]
        for split in mass_splits:
            mHch = mA + split
            print(mHch)
            vars_all = {"mass" : [], "dR" : [], "leadpt" : [], "MET" : []}
            weights_all = []
            xs = 0
            filenames = [f"{proc}/{proc}_{BP}_mHch_split_{split}/Events/run_01/unweighted_events.root:LHEF;1" for proc in procs]
            for filename, proc in zip(filenames,procs):
                try:
                    with uproot.open(filename) as f:
                        weights = f['Event']['Event.Weight'].arrays()
                        tree = f['Particle']
                        events = tree.arrays(library="ak", how="zip")
                except:
                    print(f"File {filename} not found, skipping")
                    continue
                
                part = events.Particle
                # Only want final state particles 
                part = part[part['Status'] == 1]
                branches = ['Px', 'Py', 'Pz', 'E', 'M', 'PT', 'Eta', 'Phi', 'Rapidity']
                for b in branches:
                    part[b.lower()] = part[b]
                

                part = ak.Array(part, with_name="Momentum4D")
                vars, weights = getVars(part, weights)
                proc_xs = getXS(proc, BP, split)
                # Now times by the efficiency
                eff = len(weights) / len(part)
                new_xs = proc_xs * eff

                # Now add to all the lists
                vars_all = appendToDict(vars, vars_all)
                weights_all.append(weights)
                xs += new_xs

            # If more than one file input, flatten vars_all lists
            if len(filenames) > 1:
                for var, data in vars_all.items():
                    vars_all[var] = [itm for lst in data for itm in lst]
                weights_all = [itm for lst in weights_all for itm in lst]
            variables[f"{BP}_mHch_num_{split}"] = [vars_all, weights_all, xs]

    # Now plot all of them
    save_loc = "plots/" + save_loc
    var_names = ['mass', 'dR', 'leadpt', 'MET']
    for var in var_names:
        print(f"Plotting {var}")
        settings = plot_settings[var]
        for BP, params in BP_params.items():

            os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
            plt.clf()
            mA = params[1]
            mass_splits = [1, 40, 80]
            for split in mass_splits:
                mHch = mA + split
                _ = plt.hist(variables[f"{BP}_mHch_num_{split}"][0][var], bins=60, histtype='step', 
                             alpha=0.8, range=(settings['min'], settings['max']), 
                             label=f"mHch = mA+{split}, xs={variables[f'{BP}_mHch_num_{split}'][2]:.4f}pb", 
                             weights=variables[f"{BP}_mHch_num_{split}"][1])
            plt.title(f"{settings['title']} {BP}")
            plt.yscale('log')
            plt.xlabel(settings['x'])
            plt.ylabel("count")
            plt.legend()
            plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
            plt.show()





# "lPlM_lPlMnunu_allmHch_combined"
plotDists(BP_params, ["h2h2lPlM"], "BP2_mass80_cut/lPlM_allmHch")

plotDists(BP_params, ["h2h2lPlMnunu"], "BP2_mass80_cut/lPlMnunu_allmHch")

plotDists(BP_params, ["h2h2lPlM", "h2h2lPlMnunu"], "BP2_mass80_cut/lPlM_lPlMnunu_allmHch")



















# variables = {}

# for BP in BPs:
#     print(f"BP = {BP}")
#     for lam in lams:
#         events_array = []
#         weights_array = []
#         for filename in [f"h2h2lPlMnunu/h2h2lPlMnunu_BP{BP}_lam345_{lam}", f"h2h2lPlM/h2h2lPlM_BP{BP}_lam345_{lam}"]:
#             filename = filename + "/Events/run_01/unweighted_events.root:LHEF;1"
#             try:
#                 with uproot.open(filename) as f:
#                     weights = f['Event']['Event.Weight'].arrays()
#                     tree = f['Particle']
#                     events = tree.arrays(library="ak", how="zip")
#             except:
#                 print(f"File {filename} not found, skipping")
            
#             part = events.Particle
#             # Only want final state particles 
#             part = part[part['Status'] == 1]
#             branches = ['Px', 'Py', 'Pz', 'E', 'M', 'PT', 'Eta', 'Phi', 'Rapidity']
#             for b in branches:
#                 part[b.lower()] = part[b]
            
#             # Change to 4V
#             events_array.append(part)
#             weights_array.append(weights)
        
#         weights = ak.concatenate(weights_array, axis=0)
#         part = ak.concatenate(events_array, axis=0) 
#         part = ak.Array(part, with_name="Momentum4D")
        
#         vars, weights = getVars(part, weights)
#         variables[f"{BP}_mHch_num_{split}"] = [vars, ak.flatten(weights['Event.Weight'])]

# save_loc = "lPlM_lPlMnunu_allmHch_combined"

# # Now plot all of them
# var_names = ['mass', 'dR', 'leadpt', 'MET']
# for var in var_names:
#     settings = plot_settings[var]
#     for BP in BPs:
#         os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
#         plt.clf()
#         for lam in lams:
#             _ = plt.hist(variables[f"{BP}_mHch_num_{split}"][0][var], bins=60, histtype='step', density=True, alpha=0.8, range=(settings['min'], settings['max']), label=f"lam345 = {lam}", weights=variables[f"{BP}_mHch_num_{split}"][1])
#         plt.title(f"{settings['title']} BP{BP}")
#         plt.yscale('log')
#         plt.xlabel(settings['x'])
#         plt.ylabel("count")
#         plt.legend()
#         plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
#         plt.show()

        