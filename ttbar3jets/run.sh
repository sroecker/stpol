# Create TTrees
CFGPY=../runconfs/step2_cfg.py

# 3J1T
#cmsRun $CFGPY inputFiles_load=../fileLists/TTBar.txt maxEvents=25000 outputFile=stpol_TTBar_3J1T.root nJ=3 nB=1 mc hlt mu >3J1T_25k.log 2>&1
#cmsRun $CFGPY inputFiles_load=../fileLists/SingleMu1.txt maxEvents=120000 outputFile=stpol_Data_3J1T.root nJ=3 nB=1 hlt mu >3J1T_data_120k.log 2>&1

# 3J2T
#cmsRun $CFGPY inputFiles_load=../fileLists/TTBar.txt maxEvents=80000 outputFile=stpol_TTBar_3J2T.root nJ=3 nB=2 mc hlt mu >3J2T_80k.log 2>&1
#cmsRun $CFGPY inputFiles_load=../fileLists/SingleMu1.txt maxEvents=120000 outputFile=stpol_Data_3J1T.root nJ=3 nB=2 hlt mu >3J2T_data_120k.log 2>&1
