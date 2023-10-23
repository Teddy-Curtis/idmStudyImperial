# Instead of plotting the output of Higgs DNA, I think it is better 
# to just plot the root files, as these will have more events in
import awkward as ak
import numpy as np
import vector 
import matplotlib.pyplot as plt
import mplhep as hep
plt.style.use(hep.style.CMS)
hep.cms.label(data=False, year=2017)
import uproot
import os

my_file = "/eos/user/e/ecurtis/idmFilesEOS/gridpacks/h2h2muPmuM/h2h2muPmuM/Data/h2h2muPmuM_combined_mine.root"
central_file = "root://cmsxrootd.fnal.gov//store/mc/RunIISummer20UL17NanoAODv9/IDM_MuMuHH_MA150_MH80_MHp193_TuneCP5_13TeV-madgraph-pythia8/NANOAODSIM/106X_mc2017_realistic_v9-v1/80000/324B5092-86D8-994D-97B3-48DBDCF09749.root"

my_data = uproot.open(my_file, timeout=500)['Events']
central_data = uproot.open(central_file, timeout=500)['Events']

my_data = my_data.arrays(library = "ak", how = "zip")
print(f"Number of my_data events = {len(my_data)}")
central_data = central_data.arrays(library = "ak", how = "zip")
print(f"Number of central_data events = {len(central_data)}")

dir = "/afs/cern.ch/user/e/ecurtis/idmStudyImperial/MCproduction/other/mineVsCentralProduction"



plot_settings = {
    'PT' : {
            "bins" : np.linspace(0,50,30),
            "title" : "Muon PT",
            "x" : "PT (GeV)",
            "y" : "count",
            "filename" : "Muon_PT",
            "var_name" : ("Muon", "pt"),
            "range" : [0,100]},
    'Eta' : {
            "bins" : np.linspace(-5,5,30),
            "title" : "Muon Eta",
            "x" : "Eta",
            "y" : "count",
            "filename" : "Muon_Eta",
            "var_name" : ("Muon", "eta"),
            "range" : [-3,3]},
    'MET' : {
            "bins" : np.linspace(-5,5,30),
            "title" : "MET",
            "x" : "MET",
            "y" : "count",
            "filename" : "MET",
            "var_name" : "MET_pt",
            "range" : [0,100]}
}




# Now plot
save_loc = f"{dir}"
os.makedirs(save_loc, exist_ok = True)


for var, settings in plot_settings.items():
    print(var)

    bins = settings['bins']

    # Get the hists
    try:
        my_var_data = ak.flatten(my_data[settings['var_name']])
    except:
        my_var_data = my_data[settings['var_name']]

    try:
        central_var_data = ak.flatten(central_data[settings['var_name']])
    except:
        central_var_data = central_data[settings['var_name']]

    hep.cms.label(data=False, year=2017)
    _ = plt.hist(my_var_data, label='Mine', histtype='step', bins=25, density=True, range=settings['range'])
    _ = plt.hist(central_var_data, label='Central', histtype='step', bins=25, density=True, range=settings['range'])

    plt.tight_layout()
    plt.legend()


    plt.savefig(f"{save_loc}/{settings['filename']}.pdf")
    plt.clf()
