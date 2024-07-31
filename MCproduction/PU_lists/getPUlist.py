# This gets the list of files using the dasgoclient
# To find the files for other years, follow:
# https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2F*%2F*ULPrePremix*%2F*
# Check if you're using RunIISummer19UL or RunIISummer20UL 
import subprocess

files = {
    "2016" : "/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL16_106X_mcRun2_asymptotic_v13-v1/PREMIX",
    "2017" : "/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX",
    "2018" : "/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL18_106X_upgrade2018_realistic_v11_L1v1-v2/PREMIX",
    "2022" : "/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX",
    "2022EE" : "/Neutrino_E-10_gun/Run3Summer21PrePremix-Summer22_124X_mcRun3_2022_realistic_v11-v2/PREMIX"
}


names = {
    "2016" : "16",
    "2017" : "Fall17",
    "2018" : "Autumn18",
    "2022" : "2022",
    "2022EE" : "2022EE"
}


for year, file in files.items():
    print(year)
    cmd = f'dasgoclient -query="file dataset={file}" '
    status, out = subprocess.getstatusoutput(cmd)

    with open(f"pulist_{names[year]}.txt", 'w') as f:
        f.writelines(out)