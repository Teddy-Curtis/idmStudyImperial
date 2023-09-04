"""
This is used to show the dependence on split345 that the distributions 
for the dilepton selections has.
"""

import uproot
import awkward as ak 
import vector
vector.register_awkward()
import matplotlib.pyplot as plt
import os 

BPs = [2, 5, 6]
#BPs = [5, 6]
splits = [1, 40, 80]

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
    file = f"{proc}/{proc}_BP{BP}_mHch_split_{split}/cross_section.txt"
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith('run'):
                xs, xs_err = getNumfromString(line)
                return xs

def getDilepAndExtralep(part):
    lep = part[(abs(part.PID) == 11) | (abs(part.PID) == 13)]
    dimu_events = lep[ak.num(lep[abs(lep.PID) == 13]) == 2]
    dimu = dimu_events[abs(dimu_events['PID']) == 13]
    dimu_extra_lep = dimu_events[abs(dimu_events['PID']) == 11]

    dielec_events = lep[ak.num(lep[abs(lep.PID) == 11]) == 2]
    dielec = dielec_events[abs(dielec_events['PID']) == 11]
    dielec_extra_lep = dielec_events[abs(dielec_events['PID']) == 13]

    dilep = ak.concatenate([dimu, dielec], axis=0)
    lep = ak.concatenate([dimu_extra_lep, dielec_extra_lep], axis=0)
    return dilep, lep



def getVars(part):
    # I want to get the dilepton pairs, and the third lepton
    dilep, lep = getDilepAndExtralep(part)

    vars = {}
    dilep1, dilep2 = dilep[:,0], dilep[:,1]
    dilep4v = dilep1 + dilep2
    dilepmass = dilep4v.mass
    vars['dilepmass'] = dilepmass
    dilepdR = dilep1.deltaR(dilep2)
    vars['dilepdR'] = dilepdR
    dilepPT = dilep4v.pt
    vars['dilepPT'] = dilepPT
    singlePT = lep.pt
    vars['singlePT'] = ak.flatten(singlePT)
    dilepdRlep = ak.flatten(dilep4v.deltaR(lep))
    vars['dilepdRlep'] = dilepdRlep
    weights = ak.flatten(lep.weights)
    vars['weights'] = weights

    # Now get the DM particles
    dm = part[part.PID == 35]
    # Get vector sum to find the MET 
    dm1 = dm[:,0]
    dm2 = dm[:,1]
    MET = dm1 + dm2
    vars['MET'] = MET.pt
    vars['METweights'] = dm['weights'][:,0]

    # Now get the eff
    eff = len(weights) / len(part)
    return vars, eff


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
    "dilepmass" : {
        "min" : 0,
        "max" : 100,
        "title" : "Dilep Invariant Mass",
        "x" : "Mass (GeV)"
    },
    "dilepdR" : {
        "min" : 0,
        "max" : 4,
        "title" : "dR between dileptons",
        "x" : "dR"
    },
    "dilepPT" : {
        "min" : 0,
        "max" : 140,
        "title" : "Dilepton PT",
        "x" : "PT (GeV)"
    },
    "singlePT" : {
        "min" : 0,
        "max" : 80,
        "title" : "Third Lepton PT",
        "x" : "PT (GeV)"
    },
    "dilepdRlep" : {
        "min" : 0,
        "max" : 4,
        "title" : "dR between dilepton system and Third Lep",
        "x" : "dR"
    },
    "MET" : {
        "min" : 0,
        "max" : 150,
        "title" : "MET",
        "x" : "MET (GeV)"
    }
}


def plotDists(BPs, splits, procs, save_loc):
    print(f"This is for procs = {procs}")
    variables = {}

    for BP in BPs:
        print(f"BP = {BP}")
        for split in splits:
            print(split)
            vars_all = {"dilepmass" : [], "dilepdR" : [], "dilepPT" : [], "dilepdRlep" : [], "singlePT" : [], "MET" : [], "weights" : [], "METweights" : []}
            weights_all = []
            xs = 0
            filenames = [f"{proc}/{proc}_BP{BP}_mHch_split_{split}/Events/run_01/unweighted_events.root:LHEF;1" for proc in procs]
            for filename, proc in zip(filenames,procs):
                try:
                    with uproot.open(filename) as f:
                        weights = ak.flatten(f['Event']['Event.Weight'].arrays()['Event.Weight'])
                        tree = f['Particle']
                        events = tree.arrays(library="ak", how="zip")
                except:
                    print(f"File {filename} not found, skipping")
                    continue
                
                part = events.Particle
                part['weights'] = weights

                # Only want final state particles 
                part = part[part['Status'] == 1]
                branches = ['Px', 'Py', 'Pz', 'E', 'M', 'PT', 'Eta', 'Phi', 'Rapidity']
                for b in branches:
                    part[b.lower()] = part[b]
                

                part = ak.Array(part, with_name="Momentum4D")
                vars, eff = getVars(part)
                proc_xs = getXS(proc, BP, split)
                # Now times by the efficiency
                print(f"eff for BP = {BP} and split = {split} and proc = {proc} is {eff}")
                new_xs = proc_xs * eff

                # Now add to all the lists
                vars_all = appendToDict(vars, vars_all)
                weights_all.append(weights)
                xs += new_xs

            if len(filenames) > 1:
                for var, data in vars_all.items():
                    vars_all[var] = [itm for lst in data for itm in lst]
                    
            variables[f"{BP}_{split}"] = [vars_all, xs]

    # Now plot all of them
    save_loc = "plots/" + save_loc
    var_names = ['dilepmass', 'dilepdR', 'dilepPT', 'singlePT', 'dilepdRlep', 'MET']
    for var in var_names:
        print(var)
        if var == "weights":
            continue

        settings = plot_settings[var]
        for BP in BPs:
            if not f"{BP}_{split}" in variables:
                continue
            
            os.makedirs(f"{save_loc}/{BP}", exist_ok = True)
            plt.clf()
            for split in splits:
                if var == "MET":
                    weights = variables[f"{BP}_{split}"][0]['METweights'][0]
                else:
                    weights = variables[f"{BP}_{split}"][0]['weights'][0]
                
                _ = plt.hist(variables[f"{BP}_{split}"][0][var], bins=60, histtype='step', 
                    alpha=0.8, range=(settings['min'], settings['max']), 
                    label=f"mHch = mA + {split}, xs={variables[f'{BP}_{split}'][1]:.4f}pb", weights=weights)

            plt.title(f"{settings['title']} BP{BP}")
            plt.yscale('log')
            plt.xlabel(settings['x'])
            plt.ylabel("count")
            plt.legend()
            plt.savefig(f"{save_loc}/{BP}/{var}.pdf")
            plt.show()





# "lPlM_lPlMnunu_allsplits_combined"
plotDists(BPs, splits, ["h2h2lllnu"], "uncut")








