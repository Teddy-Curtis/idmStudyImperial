# want to see how the distributions change depending on the value of mH
# i.e. for BP 21 we had "BP21" : [100, 120, 130, 0.779115, 0.0001]
# and for BP 22 we had "BP22" : [200, 220, 230, 0.779115, 0.0001]
# Hopefully this just shifts it up and down without changing the dynamcis
import uproot
import awkward as ak 
import vector
vector.register_awkward()
import matplotlib.pyplot as plt
import os 
import json 

BP_params = {"BP22" : [80, 90, 110, 0, 0.0001],
             "BP24" : [100, 110, 130, 0, 0.0001],
             "BP25" : [140, 150, 170, 0, 0.0001],
             "BP26" : [180, 190, 210, 0, 0.0001],
             "BP27" : [220, 230, 250, 0, 0.0001]}


# This gets the cross-sections of the IDM BPs
def getNumfromString(line):
    l = []
    for t in line.split():
        try:
            l.append(float(t))
        except ValueError:
            pass
    return l[0], l[1]

def getXS(proc, mH):
    file = f"{proc}/{proc}_mH_{mH}/cross_section.txt"
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
    lead_pt_cut = lep1.pt >= 15
    sublead_pt_cut = lep2.pt >= 15
    pt_cut = lead_pt_cut & sublead_pt_cut
    cut = cut & pt_cut 
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
        mH = params[0]

        vars_all = {"mass" : [], "dR" : [], "leadpt" : [], "MET" : []}
        weights_all = []
        xs = 0
        filenames = [f"{proc}/{proc}_mH_{mH}/Events/run_01/unweighted_events.root:LHEF;1" for proc in procs]
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
            proc_xs = getXS(proc, mH)
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
        variables[f"{BP}_mH_{mH}"] = [vars_all, weights_all, xs]

    # Now plot all of them
    save_loc = "plots/" + save_loc
    os.makedirs(f"{save_loc}", exist_ok = True)
    var_names = ['mass', 'dR', 'leadpt', 'MET']
    for var in var_names:
        print(f"Plotting {var}")
        settings = plot_settings[var]
        plt.clf()
        for BP, params in BP_params.items():
            mH = params[0]
            _ = plt.hist(variables[f"{BP}_mH_{mH}"][0][var], bins=60, histtype='step', density=True,
                            alpha=0.8, range=(settings['min'], settings['max']), 
                            label=f"mH={mH}, xs={variables[f'{BP}_mH_{mH}'][2]:.4f}pb", 
                            weights=variables[f"{BP}_mH_{mH}"][1])
        plt.title(f"{settings['title']}, mA-mH=10, mHch-mH=30")
        plt.yscale('log')
        plt.xlabel(settings['x'])
        plt.ylabel("count")
        plt.legend()
        plt.savefig(f"{save_loc}/{var}.pdf")
        plt.show()
    


    plt.clf()
    xses = []
    mHs = []
    for BP, params in BP_params.items():
        mH = params[0]
        mHs.append(mH)
        xs = variables[f'{BP}_mH_{mH}'][2]
        xses.append(xs)
    plt.scatter(mHs, xses)
    plt.yscale('log')
    plt.title("XS vs mH")
    plt.ylabel("Xs (pb)")
    plt.xlabel("mH")
    plt.savefig(f"{save_loc}/xses_vs_mH.pdf")
    # Also save the xses
    with open(f"{save_loc}/xses.json", 'w') as f:
        json.dump(xses, f, indent=4) 

            



plotDists(BP_params, ['h2h2lPlM'], "mass80_pt15_cut_h2h2lPlM")
plotDists(BP_params, ['h2h2lPlMnunu'], "mass80_pt15_cut_h2h2lPlMnunu")
plotDists(BP_params, ['h2h2lPlM', 'h2h2lPlMnunu'], "mass80_pt15_cut_both")