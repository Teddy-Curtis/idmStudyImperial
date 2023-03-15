# This contains functions that are usually used for openening ROOT files
import time
import uproot
import glob
import awkward as ak 

def openFile(filenames, filters):
    options = {'timeout' : 240}
    for _ in range(5):
        try:
            print('Trying to open file')
            #events = uproot.concatenate(filenames, filter_name="GenDressedLepton*", library='ak', **options)
            events = uproot.concatenate(filenames, filter_name=filters, library='ak', **options)
            print('Successfully opened file')
            return events
        except:
            print("Failed to open files, trying again in 5 seconds")
            time.sleep(5)
    print('Failed to open file')


def get2HDMaData(filenames):
    filters = ['GenDressedLepton*', 'GenPart*']
    events = openFile(filenames, filters)

    branches = ['GenDressedLepton_phi', 'GenDressedLepton_pt', 'GenDressedLepton_eta']
    leptons = events[branches]
    # First just get the events that have two leptons 
    eta = leptons.GenDressedLepton_eta
    count = ak.count(eta, axis=1, keepdims=True)
    mask = count == 2
    mask = ak.all(mask,axis=1)
    leptons = leptons[mask]


    branches = ['GenPart_eta', 'GenPart_mass', 'GenPart_phi', 'GenPart_pt', 'GenPart_genPartIdxMother', 'GenPart_pdgId', 'GenPart_status', 'GenPart_statusFlags']
    gen = events[branches]
    # I think status of 1 means that it is a final state particle so let's look at them first 
    gen_final = gen[gen.GenPart_status == 1]
    dm = gen_final[abs(gen_final.GenPart_pdgId) == 52]
    # But we want the same events as we have for the leptons (i.e. with two leptons)
    # so use the same mask as we did for the leptons
    dm = dm[mask]

    return leptons, dm




def getIDMdata(BP, process_name):
    run_name = f'{process_name}_BP{BP}'
    files = glob.glob(f'/eos/user/e/ecurtis/idmStudy/myFiles/gridpacks/{process_name}/{run_name}/wmLHEGEN*.root')
    if len(files) == 0:
        files = glob.glob(f'/eos/user/e/ecurtis/idmStudy/myFiles/gridpacks/{process_name}/{run_name}/wmNANOAODGEN*.root')

    # I want to take the latest bit of data so revserse sort and take the first value
    filename = sorted(files, reverse=True)[0] + ':Events;1'
    print(f'Filename = {filename}')
    filters = ['GenDressedLepton*', 'GenPart*']
    events = openFile(filename, filters)
    branches = ['GenDressedLepton_phi', 'GenDressedLepton_pt', 'GenDressedLepton_eta']
    leptons = events[branches]
    # First just get the events that have two leptons 
    eta = leptons.GenDressedLepton_eta
    count = ak.count(eta, axis=1, keepdims=True)
    mask = count == 2
    mask = ak.all(mask,axis=1)
    leptons = leptons[mask]

    branches = ['GenPart_eta', 'GenPart_mass', 'GenPart_phi', 'GenPart_pt', 'GenPart_genPartIdxMother', 'GenPart_pdgId', 'GenPart_status', 'GenPart_statusFlags']
    gen = events[branches]
    # I think status of 1 means that it is a final state particle so let's look at them first 
    gen_final = gen[gen.GenPart_status == 1]
    dm = gen_final[abs(gen_final.GenPart_pdgId) == 35]
    # But we want the same events as we have for the leptons (i.e. with two leptons)
    # so use the same mask as we did for the leptons
    dm = dm[mask]
    return leptons, dm


def get2HDMaEvents(filenames):
    filters = ['GenDressedLepton*', 'GenPart*']
    events = openFile(filenames, filters)
    return events

def getIDMevents(BP, process_name):
    run_name = f'{process_name}_BP{BP}'
    #files = glob.glob(f'/eos/user/e/ecurtis/idmStudy/myFiles/gridpacks/{process_name}/{run_name}/wmLHEGEN*.root')
    files = glob.glob(f'/eos/user/e/ecurtis/idmStudy/myFiles/gridpacks/{process_name}/{run_name}/wmNANOAODGEN_new_conditions*.root')
    if len(files) == 0:
        files = glob.glob(f'/eos/user/e/ecurtis/idmStudy/myFiles/gridpacks/{process_name}/{run_name}/wmNANOAODGEN*.root')

    # I want to take the latest bit of data so revserse sort and take the first value
    filename = sorted(files, reverse=True)[0] + ':Events;1'
    filters = ['GenDressedLepton*', 'GenPart*']
    events = openFile(filename, filters)
    return events