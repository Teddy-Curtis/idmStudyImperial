import uproot
import numpy as np
import awkward as ak
import matplotlib.pyplot as plt
import time
import sys
import os
import pickle
import glob
import json 
from utils.readData import get2HDMaEvents, getIDMevents
from utils.applyCuts import applyCuts, getLeptons, getDM

process_name = 'h2h2lPlM_lem'




mH = int(sys.argv[1])
mA = int(sys.argv[2])
print(f'mH = {mH}, mA = {mA}')

os.environ["X509_USER_PROXY"] = "/afs/cern.ch/user/e/ecurtis/cms.proxy"
print(os.environ["X509_USER_PROXY"]) 

class scale2HDMa:
    def __init__(self, num_samples, lumi):
        self.total = num_samples
        self.lumi  = lumi
    def scale(self, data, params):
        mH = params['mH']
        mA = params['mA']
        # First I need to read in the cross-section
        with open("utils/2HDMa_XS.txt", "r") as fp:
            # Load the dictionary from the file
            XS_dict = json.load(fp)
        name = f"mH-{mH}_mA-{mA}"
        xs = XS_dict[name]['xsec'] * 1000 # convert to fb
        expected = xs * lumi
        weight = expected / self.total
        num_events = len(data)
        return weight*np.ones(num_events), xs
        


class scaleIDM:
    def __init__(self, num_samples, lumi):
        self.total = num_samples
        self.lumi  = lumi

    def scale(self, data, params):
        BP = params['BP']
        # First I need to read in the cross-section
        with open("utils/IDM_XS.txt", "r") as fp:
            # Load the dictionary from the file
            XS_dict = json.load(fp)
        xs = XS_dict[f'BP{BP}']['xsec'] * 1000 # convert to fb
        expected = xs * lumi
        weight = expected / self.total
        num_events = len(data)
        return weight*np.ones(num_events), xs


def invMassLep(leptons):
    pt1 = leptons.GenDressedLepton_pt[:,0]
    pt2 = leptons.GenDressedLepton_pt[:,1]
    eta1 = leptons.GenDressedLepton_eta[:,0]
    eta2 = leptons.GenDressedLepton_eta[:,1]
    phi1 = leptons.GenDressedLepton_phi[:,0]
    phi2 = leptons.GenDressedLepton_phi[:,1]

    inv_M = np.sqrt(2*pt1*pt2*((np.cosh(eta1 - eta2)) - (np.cos(phi1 - phi2))))
    return inv_M


def plotLeptonInvMass(leptons, lep_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    inv_M = invMassLep(leptons)
    inv_M_idm = invMassLep(lep_idm)
    nbins = 100
    _ = plt.hist(inv_M, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(inv_M_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"Lepton inv M: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('Invariant Mass (GeV)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_leptonInvMass.png")
    plt.clf()


def leptonPT(leptons, return_vec = False):
    phi1 = leptons['GenDressedLepton_phi'][:,0]
    phi2 = leptons['GenDressedLepton_phi'][:,1]
    pt1 = leptons['GenDressedLepton_pt'][:,0]
    pt2 = leptons['GenDressedLepton_pt'][:,1]

    lep_PT_vec = np.array([pt1*np.cos(phi1) + pt2*np.cos(phi2), pt1*np.sin(phi1) + pt2*np.sin(phi2)])
    PT_abs = np.linalg.norm(lep_PT_vec, axis=0)
    if return_vec:
        return lep_PT_vec, PT_abs
    else:
        return PT_abs


def plotLeptonPTabs(leptons, lep_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    PT_abs_2HDMa = leptonPT(leptons)
    PT_abs_idm = leptonPT(lep_idm)

    nbins = 100
    _ = plt.hist(PT_abs_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(PT_abs_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"Dilepton PT: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('PT (GeV)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_dileptonPT.png")
    plt.clf()


def PTmiss(dm, return_vec = False):
    dm_phi1 = dm['GenPart_phi'][:,0]
    dm_phi2 = dm['GenPart_phi'][:,1]
    dm_pt1 = dm['GenPart_pt'][:,0]
    dm_pt2 = dm['GenPart_pt'][:,1]
    MET_vec = np.array([dm_pt1*np.cos(dm_phi1) + dm_pt2*np.cos(dm_phi2), dm_pt1*np.sin(dm_phi1) + dm_pt2*np.sin(dm_phi2)])
    tot_MET = np.linalg.norm(MET_vec, axis=0)
    if return_vec:
        return MET_vec, tot_MET
    else:
        return tot_MET

def plotPTmiss(dm, dm_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(dm, params)
    idm_scale, xs_idm = scaler_idm.scale(dm_idm, params)
    PTmiss_2HDMa = PTmiss(dm)
    PTmiss_idm = PTmiss(dm_idm) 
    
    nbins = 100
    _ = plt.hist(PTmiss_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(PTmiss_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"PT_miss: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('PT (GeV)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_PTmiss.png")
    plt.clf()

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))

def transverseMass(leptons, dm):
    # First get transverse mass for the 2HDMa model
    lep_PT_vec, lep_PT_abs = leptonPT(leptons, return_vec=True)
    PTmiss_vec, PTmiss_abs = PTmiss(dm, return_vec=True)
    
    angles = []
    for i in range(len(lep_PT_vec[0])):
        vec1 = np.array([lep_PT_vec[0,i], lep_PT_vec[1,i]])
        vec2 = np.array([PTmiss_vec[0,i], PTmiss_vec[1,i]])
        angle = angle_between(vec1, vec2)
        angles.append(angle)
    # Now get the transverse mass 
    M = np.sqrt(2*lep_PT_abs*PTmiss_abs*(1 - np.cos(angles)))
    return M

def plotTransverseMass(leptons, dm, lep_idm, dm_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    MT_2HDMa = transverseMass(leptons, dm)
    MT_idm = transverseMass(lep_idm, dm_idm)

    nbins = 100
    _ = plt.hist(MT_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(MT_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"Transverse Mass: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('Transverse Mass (GeV)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_MT.png")
    plt.clf()


def deltaPhi_PTll_PTmiss(leptons, dm):
    PT_vec, _ = leptonPT(leptons, return_vec=True)
    PTmiss_vec, _ = PTmiss(dm, return_vec=True)
    angles = []
    for i in range(len(PT_vec[0])):
        vec1 = np.array([PT_vec[0,i], PT_vec[1,i]])
        vec2 = np.array([PTmiss_vec[0,i], PTmiss_vec[1,i]])
        angle = angle_between(vec1, vec2)
        angles.append(angle)
    return angles
    

def plotDeltaPhi_PTll_PTmiss(leptons, dm, lep_idm, dm_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    # Find first for 2HDMa model
    deltaPhi_2HDMa = deltaPhi_PTll_PTmiss(leptons, dm)
    deltaPhi_idm = deltaPhi_PTll_PTmiss(lep_idm, dm_idm)

    nbins = 100
    _ = plt.hist(deltaPhi_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(deltaPhi_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"DeltaPhi between PT_ll and PT_miss: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('Delta Phi (Rad)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_deltaPhi_PTll_PTmiss.png")
    plt.clf()

def balanceRatio(leptons, dm):
    PT_abs = leptonPT(leptons)
    PTmiss_abs = PTmiss(dm)
    balanceRatio = abs(PTmiss_abs - PT_abs) / PT_abs
    return balanceRatio


def plotBalanceRatio(leptons, dm, lep_idm, dm_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    BR_2HDMa = balanceRatio(leptons, dm)
    BR_idm = balanceRatio(lep_idm, dm_idm)

    nbins = 100
    _ = plt.hist(BR_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(BR_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"Balance Ratio: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('Balance Ratio')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_balance_ratio.png")
    plt.clf()

def leptonDeltaR(leptons):
    phi1 = leptons['GenDressedLepton_phi'][:,0]
    phi2 = leptons['GenDressedLepton_phi'][:,1]
    eta1 = leptons['GenDressedLepton_eta'][:,0]
    eta2 = leptons['GenDressedLepton_eta'][:,1]
    deltaR = np.sqrt((phi1 - phi2)**2 + (eta1 - eta2)**2)
    return deltaR

def plotLeptonDeltaR(leptons, lep_idm, params):
    scaler_idm, scaler_2hdma = params['scaler_IDM'], params['scaler_2HDMa']
    hdma_scale, xs_hdma = scaler_2hdma.scale(leptons, params)
    idm_scale, xs_idm = scaler_idm.scale(lep_idm, params)
    deltaR_2HDMa = leptonDeltaR(leptons)
    deltaR_idm = leptonDeltaR(lep_idm)

    nbins = 100
    _ = plt.hist(deltaR_2HDMa, bins=nbins, weights=hdma_scale, label=f'2HDMa, xs={xs_hdma:0.4}', histtype='step')
    _ = plt.hist(deltaR_idm, bins=nbins, weights=idm_scale, label=f'IDM, xs={xs_idm:0.4}', histtype='step')
    plt.legend()
    plt.title(f"Lepton DeltaR: mH={params['mH']}, mA={params['mA']}, BP={params['BP']}, Lumi=137fb^-1", fontsize=10)
    plt.xlabel('Delta R (Rad)')
    plt.ylabel('Count')
    plt.savefig(f"/vols/cms/emc21/idmStudy/recast/plots/idmVs2hdma/idm_v_2HDMa_mH{params['mH']}_mA{params['mA']}_BP{params['BP']}_lepton_deltaR.png")
    plt.clf()





lumi = 137
events_2HDMa = get2HDMaEvents(mH, mA)
scaler_2HDMa = scale2HDMa(len(events_2HDMa), lumi)
print(f'Applying cuts to 2hdma events:')
cut_events_2HDMa = applyCuts(events_2HDMa, dm_pdgId=52)
leptons = getLeptons(cut_events_2HDMa)
dm = getDM(cut_events_2HDMa, dm_pdgId=52)
# Now I need to loop over ONLY the BPs with on-shell Zs to compare
idm_on_shell = [8, 10, 12, 13, 14, 18, 19, 20, 21, 24]
for BP in idm_on_shell:
    # Now I need to get the data for the idm
    events_IDM = getIDMevents(BP, process_name)
    scaler_IDM = scaleIDM(len(events_IDM), lumi)
    print(f'Applying cuts to idm events for BP {BP}:')
    cut_events_idm = applyCuts(events_IDM, dm_pdgId=35)
    lep_idm = getLeptons(cut_events_idm)
    dm_idm = getDM(cut_events_idm, dm_pdgId=35)

    params = {'mH' : mH, 'mA' : mA, 'BP' : BP,'process_name' : process_name,
            'scaler_IDM' : scaler_IDM, 'scaler_2HDMa' : scaler_2HDMa}
    # Now I want to plot everything
    plotLeptonInvMass(leptons, lep_idm, params)
    plotLeptonPTabs(leptons, lep_idm, params)
    plotPTmiss(dm, dm_idm, params)
    plotTransverseMass(leptons, dm, lep_idm, dm_idm, params)
    plotDeltaPhi_PTll_PTmiss(leptons, dm, lep_idm, dm_idm, params)
    plotBalanceRatio(leptons, dm, lep_idm, dm_idm, params)
    plotLeptonDeltaR(leptons, lep_idm, params)
    

print("Finished making all the plots!")
