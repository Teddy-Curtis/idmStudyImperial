# Here we will take in the data and apply the cuts
import awkward as ak 
import numpy as np

def getLeptons(events):
    branches = ['GenDressedLepton_phi', 'GenDressedLepton_pt', 'GenDressedLepton_eta']
    leptons = events[branches]
    return leptons

def getDM(events, dm_pdgId):
    branches = ['GenPart_eta', 'GenPart_mass', 'GenPart_phi', 'GenPart_pt', 'GenPart_genPartIdxMother', 'GenPart_pdgId', 'GenPart_status', 'GenPart_statusFlags']
    gen = events[branches]
    # I think status of 1 means that it is a final state particle so let's look at them first 
    gen_final = gen[gen.GenPart_status == 1]
    dm = gen_final[abs(gen_final.GenPart_pdgId) == dm_pdgId]
    return dm

def getJets(events):
    branches = ['GenJet_eta', 'GenJet_hadronFlavour', 'GenJet_mass', 'GenJet_partonFlavour', 'GenJet_phi', 'GenJet_pt']
    jets = events[branches]
    return jets

def cutNleptons(events):
    print('cutNleptons:')
    # Take events with only 2 leptons
    leptons = getLeptons(events)
    eta = leptons.GenDressedLepton_eta
    count = ak.count(eta, axis=1, keepdims=True)
    mask = count == 2
    mask = ak.all(mask,axis=1)
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events 

def cutLeadingSubleadingLeptonPT(events):
    print('cutLeadingSubleadingLeptonPT:')
    # I only want to use events where the leading lepton 
    # has > 25 GeV and the subleading lepton has > 20
    # This works based on the idea that True*True=True
    # True*False=False and False*False=False
    leptons = getLeptons(events)
    lead_pt = leptons.GenDressedLepton_pt[:,0]
    sub_pt = leptons.GenDressedLepton_pt[:,1]
    lead_mask = lead_pt > 25
    sub_mask = sub_pt > 20
    mask = lead_mask * sub_mask
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events


def invMassLep(leptons):
    pt1 = leptons.GenDressedLepton_pt[:,0]
    pt2 = leptons.GenDressedLepton_pt[:,1]
    eta1 = leptons.GenDressedLepton_eta[:,0]
    eta2 = leptons.GenDressedLepton_eta[:,1]
    phi1 = leptons.GenDressedLepton_phi[:,0]
    phi2 = leptons.GenDressedLepton_phi[:,1]

    inv_M = np.sqrt(2*pt1*pt2*((np.cosh(eta1 - eta2)) - (np.cos(phi1 - phi2))))
    return inv_M


def cutDilepton_mass(events):
    print('cutDilepton_mass:')
    # Cut that |m_ll - m_Z| < 15 GeV
    M_Z = 91.1876
    leptons = getLeptons(events)
    # first get the lepton invariant mass
    inv_M = invMassLep(leptons)
    mask = abs(inv_M - M_Z) < 15
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events

# def cutnumJets(events):


def dileptonPT(leptons, return_vec = False):
    phi1 = leptons['GenDressedLepton_phi'][:,0]
    phi2 = leptons['GenDressedLepton_phi'][:,1]
    pt1 = leptons['GenDressedLepton_pt'][:,0]
    pt2 = leptons['GenDressedLepton_pt'][:,1]

    x = np.array(pt1*np.cos(phi1) + pt2*np.cos(phi2))
    y = np.array(pt1*np.sin(phi1) + pt2*np.sin(phi2))
    PT_vec = np.stack((x,y), axis=1)
    PT_abs = np.linalg.norm(PT_vec, axis=1)
    if return_vec:
        return PT_vec, PT_abs
    else:
        return PT_abs

def cutDileptonPT(events):
    print('cutDileptonPT:')
    leptons = getLeptons(events)
    PT_abs = dileptonPT(leptons)
    mask = PT_abs > 60
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events

def PTmiss(dm, return_vec = False):
    dm_phi1 = dm['GenPart_phi'][:,0]
    dm_phi2 = dm['GenPart_phi'][:,1]
    dm_pt1 = dm['GenPart_pt'][:,0]
    dm_pt2 = dm['GenPart_pt'][:,1]
    x = np.array(dm_pt1*np.cos(dm_phi1) + dm_pt2*np.cos(dm_phi2))
    y = np.array(dm_pt1*np.sin(dm_phi1) + dm_pt2*np.sin(dm_phi2))
    MET_vec = np.stack((x,y), axis=1)
    tot_MET = np.linalg.norm(MET_vec, axis=1)
    if return_vec:
        return MET_vec, tot_MET
    else:
        return tot_MET

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


def cutDeltaPhiPTllPTmiss(events, dm_pdgId):
    print(f'cutDeltaPhiPTllPTmiss:')
    leptons = getLeptons(events)
    dm = getDM(events, dm_pdgId)
    dilepton_PT, _ = dileptonPT(leptons, return_vec=True)
    PT_miss, _ = PTmiss(dm, return_vec=True)
    angles = []
    for lep_vec, PT_vec in zip(dilepton_PT, PT_miss):
        angle = angle_between(lep_vec, PT_vec)
        angles.append(angle)
    angles = np.array(angles)
    mask = angles > 2.6
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events



def cutBalanceRatio(events, dm_pdgId):
    print('cutBalanceRatio:')
    leptons = getLeptons(events)
    dilepton_PT = dileptonPT(leptons)

    dm = getDM(events, dm_pdgId)
    PT_miss = PTmiss(dm)

    balanceRatio = abs(PT_miss - dilepton_PT) / dilepton_PT
    mask = balanceRatio < 0.4
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events

def cutLeptonDeltaR(events):
    print('cutLeptonDeltaR:')
    leptons = getLeptons(events)
    phi1 = leptons['GenDressedLepton_phi'][:,0]
    phi2 = leptons['GenDressedLepton_phi'][:,1]
    eta1 = leptons['GenDressedLepton_eta'][:,0]
    eta2 = leptons['GenDressedLepton_eta'][:,1]
    deltaR = np.sqrt((phi1 - phi2)**2 + (eta1 - eta2)**2)

    mask = deltaR < 1.8
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events

def cutPTmiss(events, dm_pdgId):
    print('cutPTmiss:')
    dm = getDM(events, dm_pdgId)
    PT_miss = PTmiss(dm)
    mask = PT_miss > 80
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events

def jetPT(jets, return_vec = False):
    phi1 = jets['GenJet_phi'][:,0]
    pt1 = jets['GenJet_pt'][:,0]
    x = np.array(pt1*np.cos(phi1))
    y = np.array(pt1*np.sin(phi1))
    jet_vec = np.stack((x,y), axis=1)
    jet_vec_abs = np.linalg.norm(jet_vec, axis=1)
    if return_vec:
        return jet_vec, jet_vec_abs
    else:
        return jet_vec_abs
    

def cutNjets(events, njets):
    print('cutNjets:')
    jets = getJets(events)
    # Want to split into two categories: 0 jet > 30GeV
    # and 1 jet > 30 GeV, for jet |eta|<4.7
    jet_pt = jets.GenJet_pt
    pt_mask = jet_pt > 30
    jet_eta = jets.GenJet_eta
    eta_mask = abs(jet_eta) < 4.7
    # As I need both criteria satisfied, I can times
    # them together, and only elements that equal True
    # are jets with pt>30 and |eta|<4.7
    mask = pt_mask * eta_mask
    # This finds how many jets in an event are over 30 GeV
    num_over_30 = ak.sum(mask, axis=1)
    # Get the indexes for events with n jets 
    # that have over 30 GeV
    n_jets_idxs = np.argwhere(num_over_30 == njets)
    print(f'Percentage of events taken out = {((len(mask) - len(n_jets_idxs)) / len(mask)) * 100:.2f}')
    events = events[n_jets_idxs]
    return events


def cutDeltaPhiPTjetPTmiss(events, dm_pdgId):
    print(f'cutDeltaPhiPTjetPTmiss:')
    dm = getDM(events, dm_pdgId)
    PT_miss, _ = PTmiss(dm, return_vec=True)
    jets = getJets(events)
    jet_PT, _ = jetPT(jets, return_vec=True)
    angles = []
    for jet_vec, PT_vec in zip(jet_PT, PT_miss):
        angle = angle_between(jet_vec, PT_vec)
        angles.append(angle)
    angles = np.array(angles)
    mask = angles > 0.5
    print(f'Percentage of events taken out = {((len(mask) - np.sum(mask)) / len(mask)) * 100:.2f}')
    events = events[mask]
    return events


def applyCuts(events, dm_pdgId, njets):
    # Here cuts is a dictionary with all the specified cuts
    events = cutNjets(events, njets)
    events = cutNleptons(events)
    events = cutDeltaPhiPTjetPTmiss(events, dm_pdgId)
    events = cutLeadingSubleadingLeptonPT(events)
    events = cutDilepton_mass(events)
    events = cutDileptonPT(events)
    events = cutDeltaPhiPTllPTmiss(events, dm_pdgId)
    events = cutBalanceRatio(events, dm_pdgId)
    events = cutLeptonDeltaR(events)
    events = cutPTmiss(events, dm_pdgId)
    return events
