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

BPs = [2, 5]

# Params in the form: MH, MA, MHPM, Lam2, Lam345, wh3, whP with wX being the width of the particle
BP_params = {"BP2" : [65, 71.525, 112.85, 0.779115, 0.0, 8.33387e-09, 0.00027545884846],
    "BP5" : [72.14, 109.548, 154.761, 0.0125664, 0.0, 4.46479e-05, 0.0121323319543],
    "BP6" : [76.55, 134.563, 174.367, 1.94779, 0.0, 0.000400455, 0.141594920929]}
# BP_params = {"BP2" : [65, 71.525, 112.85, 0.779115, 0.0, 8.33387e-09, 0.00027545884846],
#     "BP5" : [72.14, 109.548, 154.761, 0.0125664, 0.0, 4.46479e-05, 0.0121323319543]}

def getVars(part, weights):
    lep = part[(abs(part.PID) == 11) | (abs(part.PID) == 13)]
    vars = {}
    lep1, lep2 = lep[:,0], lep[:,1]
    dilep = lep1 + lep2
    cut = lep1['PID'] == -lep2['PID']
    # mass = dilep.mass
    # mass_cut = mass < 80
    # cut = cut & mass_cut
    lep = lep[cut]

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
    return vars, weights
    
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
        "max" : 200,
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
        mHchs = [mA + 1, mA + 40, mA + 80]
        for i, mHch in enumerate(mHchs):
            events_array = []
            weights_array = []
            filenames = [f"{proc}/{proc}_BP{BP}_mHch_num_{i}/Events/run_01/unweighted_events.root:LHEF;1" for proc in procs]
            for filename in filenames:
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
                
                # Change to 4V
                events_array.append(part)
                weights_array.append(weights)
            
            weights = ak.concatenate(weights_array, axis=0)
            events = ak.concatenate(events_array, axis=0) 
            events = ak.Array(events, with_name="Momentum4D")
            
            vars, weights = getVars(events, weights)
            variables[f"{BP}_mHch_num_{i}"] = [vars, ak.flatten(weights['Event.Weight'])]

    # Now plot all of them
    var_names = ['mass', 'dR', 'leadpt', 'MET']
    for var in var_names:
        settings = plot_settings[var]
        for BP, params in enumerate(BP_params):
            os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
            plt.clf()
            mA = params[1]
            mHchs = [mA + 1, mA + 40, mA + 80]
            for i, mHch in enumerate(mHchs):
                _ = plt.hist(variables[f"{BP}_mHch_num_{i}"][0][var], bins=60, histtype='step', density=True, alpha=0.8, range=(settings['min'], settings['max']), label=f"mHch = {mHch}", weights=variables[f"{BP}_mHch_num_{i}"][1])
            plt.title(f"{settings['title']} BP{BP}")
            plt.yscale('log')
            plt.xlabel(settings['x'])
            plt.ylabel("count")
            plt.legend()
            plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
            plt.show()


plotDists(BP_params, ["h2h2lPlM"], "h2h2lPlM_allMasses")



# First do with just h2h2lPlM then h2h2lPlMnunu, then combine

# for proc in ["h2h2lPlMnunu", "h2h2lPlM"]:
#     variables = {}
#     for BP, params in BP_params.items():
#         print(f"BP = {BP}")
#         mA = params[1]
#         mHchs = [mA + 1, mA + 50, mA + 100]
#         for i, mHch in enumerate(mHchs):
#             events_array = []
#             weights_array = []
#             filename = f"{proc}/{proc}_{BP}_mHch_num_{i}/Events/run_01/unweighted_events.root:LHEF;1"
#             with uproot.open(filename) as f:
#                 weights = f['Event']['Event.Weight'].arrays()
#                 tree = f['Particle']
#                 events = tree.arrays(library="ak", how="zip")
#                 part = events.Particle
#                 # Only want final state particles 
#                 part = part[part['Status'] == 1]
#                 branches = ['Px', 'Py', 'Pz', 'E', 'M', 'PT', 'Eta', 'Phi', 'Rapidity']
#                 for b in branches:
#                     part[b.lower()] = part[b]
                
#                 # Change to 4V
#                 events_array.append(part)
#                 weights_array.append(weights)
#             weights = ak.concatenate(weights_array, axis=0)
#             part = ak.concatenate(events_array, axis=0) 
#             part = ak.Array(part, with_name="Momentum4D")
            
#             vars, weights = getVars(part, weights)
#             variables[f"{BP}_mHch_num_{i}"] = [vars, ak.flatten(weights['Event.Weight'])]

#     save_loc = f"{proc}_AllmHch_combined"

#     # Now plot all of them
#     var_names = ['mass', 'dR', 'leadpt', 'MET']
#     for var in var_names:
#         settings = plot_settings[var]
#         for BP, params in BP_params.items():
#             os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
#             plt.clf()
#             mA = params[1]
#             mHchs = [mA + 1, mA + 50, mA + 100]
#             for i, mHch in enumerate(mHchs):
#                 _ = plt.hist(variables[f"{BP}_mHch_num_{i}"][0][var], bins=60, histtype='step', density=True, alpha=0.8, range=(settings['min'], settings['max']), label=f"mHch = {mHch}", weights=variables[f"{BP}_mHch_num_{i}"][1])
#             plt.title(f"{settings['title']} BP{BP} mA={mA}")
#             plt.yscale('log')
#             plt.xlabel(settings['x'])
#             plt.ylabel("count")
#             plt.legend()
#             plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
#             plt.show()

        

# variables = {}

# for BP, params in BP_params.items():
#     print(f"BP = {BP}")
#     mA = params[1]
#     mHchs = [mA + 1, mA + 50, mA + 100]
#     for i, mHch in enumerate(mHchs):
#         events_array = []
#         weights_array = []
#         for filename in [f"h2h2lPlMnunu/h2h2lPlMnunu_{BP}_mHch_num_{i}", f"h2h2lPlM/h2h2lPlM_{BP}_mHch_num_{i}"]:
#             filename = filename + "/Events/run_01/unweighted_events.root:LHEF;1"
#             with uproot.open(filename) as f:
#                 weights = f['Event']['Event.Weight'].arrays()
#                 tree = f['Particle']
#                 events = tree.arrays(library="ak", how="zip")
#                 part = events.Particle
#                 # Only want final state particles 
#                 part = part[part['Status'] == 1]
#                 branches = ['Px', 'Py', 'Pz', 'E', 'M', 'PT', 'Eta', 'Phi', 'Rapidity']
#                 for b in branches:
#                     part[b.lower()] = part[b]
                
#                 # Change to 4V
#                 events_array.append(part)
#                 weights_array.append(weights)
#         weights = ak.concatenate(weights_array, axis=0)
#         part = ak.concatenate(events_array, axis=0) 
#         part = ak.Array(part, with_name="Momentum4D")
        
#         vars, weights = getVars(part, weights)
#         variables[f"{BP}_mHch_num_{i}"] = [vars, ak.flatten(weights['Event.Weight'])]

# save_loc = "lPlM_lPlMnunu_allLams_combined"

# # Now plot all of them
# var_names = ['mass', 'dR', 'leadpt', 'MET']
# for var in var_names:
#     settings = plot_settings[var]
#     for BP, params in BP_params.items():
#         os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
#         plt.clf()
#         mA = params[1]
#         mHchs = [mA + 1, mA + 50, mA + 100]
#         for i, mHch in enumerate(mHchs):
#             _ = plt.hist(variables[f"{BP}_mHch_num_{i}"][0][var], bins=60, histtype='step', density=True, alpha=0.8, range=(settings['min'], settings['max']), label=f"mHch = {mHch}", weights=variables[f"{BP}_mHch_num_{i}"][1])
#         plt.title(f"{settings['title']} BP{BP} mA={mA}")
#         plt.yscale('log')
#         plt.xlabel(settings['x'])
#         plt.ylabel("count")
#         plt.legend()
#         plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
#         plt.show()

        