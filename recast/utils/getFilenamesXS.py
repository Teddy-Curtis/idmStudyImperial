import pickle
import subprocess
import json

# This first bit gets the filenames of the 2HDMa files
files = {}

for mH in range(200,1500,100):
    for mA in range(100, mH, 100):
        if (mA <= 500) and (mH != 1100) and (mH != 1300):
            print(mH, mA)
            dataset = f"/Pseudoscalar2HDM_MonoZLL_mScan_mH-{mH}_ma-{mA}/RunIIFall17NanoAODv7-PU2017_12Apr2018_Nano02Apr2020_102X_mc2017_realistic_v8-v1/NANOAODSIM"
            cmd = f"dasgoclient -query 'file dataset={dataset}'"
            status, out = subprocess.getstatusoutput(cmd)
            filenames = out.split('\n')
            filenames = ["root://cmsxrootd.fnal.gov///store/test/xrootd/T1_ES_PIC" + file + ":Events;1" for file in filenames]
            files[f'mH{mH}_mA{mA}'] = filenames

#print(files)
with open('2HDMa_files.json', 'w') as fp:
    json.dump(files, fp, indent=4)

# This gets the cross-sections of the IDM BPs
def getNumfromString(line):
    l = []
    for t in line.split():
        try:
            l.append(float(t))
        except ValueError:
            pass
    return l[0], l[1]

process_name = 'h2h2lPlM_lem'
idm_on_shell = [8, 10, 12, 13, 14, 18, 19, 20, 21, 24]
my_dict = {'BP' : ['xsec (pb)', 'error (pb)']}
for BP in idm_on_shell:
    run_name = f'{process_name}_BP{BP}'
    file = f'//vols/cms/emc21/idmStudy/myFiles/gridpacks/{process_name}_CMSSW_10_6_19/{run_name}/{run_name}.log'
    with open(file) as f:
        lines = f.readlines()
        for line in lines:
            if "Cross-section" in line:
                xs, xs_err = getNumfromString(line)
                xs = xs

                my_dict[f'BP{BP}'] = {'XS' : xs, 'error' : xs_err}

print(my_dict)

with open("IDM_XS.json", "w") as fp:
    json.dump(my_dict, fp, indent=4)  # encode dict into JSON

