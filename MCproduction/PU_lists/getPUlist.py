# This gets the list of files using the dasgoclient
# To find the files for other years, follow:
# https://cmsweb.cern.ch/das/request?view=list&limit=50&instance=prod%2Fglobal&input=dataset%3D%2F*%2F*ULPrePremix*%2F*
# Check if you're using RunIISummer19UL or RunIISummer20UL 
import subprocess

files = {
    "2017" : "/Neutrino_E-10_gun/RunIISummer20ULPrePremix-UL17_106X_mc2017_realistic_v6-v3/PREMIX"
}


names = {
    "2017" : "Fall17"
}


for year, file in files.items():
    print(year)
    cmd = f'dasgoclient -query="file dataset={file}" '
    status, out = subprocess.getstatusoutput(cmd)

    with open(f"pulist_{names[year]}.txt", 'w') as f:
        f.writelines(out)