import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import uproot
import mplhep as hep
hep.style.use('CMS')
import os

# This loops over each BP and outputs a plot for different 
# variables for different particles. 

# define the process and the number of BPs
process = 'h2h2lPlM_l_e_mu'
num_BPs = 21
base_dir = '/vols/cms/emc21/FCC/MadGraph_files/distributions'



def H_PT_scalarSum(H_data, dir):
    mean = H_data['Particle.PT'].mean()
    std = H_data['Particle.PT'].std()
    nbins = 100 
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(H_data['Particle.PT'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Scalar sum of H PTs')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/H_PT_scalarSum.jpeg', bbox_inches='tight')
    plt.close()


def H_PT_vectorSum(H_data, dir):
    grouped = H_data.groupby(level=0).sum()
    grouped['PT_tot'] = np.sqrt(grouped['Particle.Px']**2 + grouped['Particle.Py']**2)
    nbins = 100
    mean = grouped['PT_tot'].mean()
    std = grouped['PT_tot'].std()
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(grouped['PT_tot'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Vector sum of H PTs')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/H_PT_vectorSum.jpeg', bbox_inches='tight')
    plt.close()



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

def getAngle(df):
    vs = df[['Particle.Px', 'Particle.Py', 'Particle.Pz']].to_numpy()
    angle = angle_between(vs[0,:2], vs[1,:2])
    return angle


def H_angleDiff(H_data, dir):
    g = H_data.groupby('entry')
    angles = g.apply(getAngle)
    mean = np.mean(angles)
    std = np.std(angles)
    nbins = 100
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(angles, bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Angle between Hs')
    plt.xlabel(f'Angle (radians)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/H_angleDiff.jpeg', bbox_inches='tight')
    plt.close()


def A_PT(A_data, dir):
    mean = A_data['Particle.PT'].mean()
    std = A_data['Particle.PT'].std()
    nbins = 100
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(A_data['Particle.PT'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'A PT')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/A_PT.jpeg', bbox_inches='tight')
    plt.close()

def HA_PT_vectorSum(data, dir):
    inert_data = data[(data['Particle.PID'] == 35) | (data['Particle.PID'] == 36)]
    # This groups them into different events, then sums their Px, Py etc
    # Can then find the abs of this to get the actual E_miss
    inert_data = inert_data.groupby(level=0).sum()
    inert_data['PT_tot'] = np.sqrt(inert_data['Particle.Px']**2 + inert_data['Particle.Py']**2)
    mean = inert_data['PT_tot'].mean()
    std = inert_data['PT_tot'].std()
    nbins = 100
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(inert_data['PT_tot'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Vector sum of H and A PT')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/HA_PT_vectorSum.jpeg', bbox_inches='tight')
    plt.close()


def lepton_PT(lepton_data, dir):
    mean = lepton_data['Particle.PT'].mean()
    std = lepton_data['Particle.PT'].std()
    nbins = 100
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(lepton_data['Particle.PT'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Lepton PT')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/lepton_PT.jpeg', bbox_inches='tight')
    plt.close()

def lepton_angleDiff(lepton_data, dir):
    g = lepton_data.groupby('entry')
    angles = g.apply(getAngle)
    mean = np.mean(angles)
    std = np.std(angles)
    nbins = 100
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(angles, bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Angle Between Leptons')
    plt.xlabel(f'Angle (radians)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/lepton_angleDiff.jpeg', bbox_inches='tight')
    plt.close()

def jet_PT(jet_data, dir):
    # Plot of PT
    nbins = 100
    mean = jet_data['Particle.PT'].mean()
    std = jet_data['Particle.PT'].std()
    plt.figure(figsize=(8,6))
    plt.tight_layout()
    plt.hist(jet_data['Particle.PT'], bins=nbins, label=f'$\mu={mean:0.2f}$, $\sigma={std:0.2f}$')
    plt.title(f'Jet PT')
    plt.xlabel(f'PT (GeV)')
    plt.ylabel(f'Counts')
    plt.legend()
    plt.savefig(f'{dir}/jet_PT.jpeg', bbox_inches='tight')
    plt.close()


for i in range(1, 22):
    print(f'Making plots for BP{i}')
    BP = f'BP{i}'
    plot_dir = f'{base_dir}/{process}/{BP}/plots'

    try :
        os.mkdir(plot_dir)
    except:
        print('Directory already made.')

    data_dir = f'{base_dir}/{process}/{BP}/{process}_{BP}/Events/run_01/unweighted_events.root'
    
    file = uproot.open(data_dir)
    tree = file['LHEF']
    tree = tree['Particle']
    print(tree.keys())
    data = tree.arrays(['Particle.PID', 'Particle.Px','Particle.Py', 'Particle.Pz', 'Particle.PT', 'Particle.E', 'Particle.Eta'], library='pd')

    # Now plot everything
    H_data = data[(data['Particle.PID'] == 35)]
    H_PT_scalarSum(H_data, plot_dir)
    H_PT_vectorSum(H_data, plot_dir)
    H_angleDiff(H_data, plot_dir)

    A_data = data[(data['Particle.PID'] == 36)]
    A_PT(A_data, plot_dir)

    HA_PT_vectorSum(data, plot_dir)

    lepton_data = data[(abs(data['Particle.PID']) == 11) | (abs(data['Particle.PID']) == 13)]
    lepton_PT(lepton_data, plot_dir)
    lepton_angleDiff(lepton_data, plot_dir)

    # Get rid of the quarks from the protons that go down the beampipe 
    jet_data = data[(abs(data['Particle.Eta']) < 900)]
    # Now pick out the quarks
    quarks = [1,2,3,4,5]
    jet_data = jet_data[abs(jet_data['Particle.PID']).isin(quarks)]
    jet_PT(jet_data, plot_dir)