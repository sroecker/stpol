CFGPY=../runconfs/step2_cfg.py

cmsRun $CFGPY inputFiles_load=../fileLists/TTBar.txt maxEvents=10000 outputFile=stpol_TTBar_3J0T.root nJ=3 nB=0 mc hlt
cmsRun $CFGPY inputFiles_load=../fileLists/TTBar.txt maxEvents=10000 outputFile=stpol_TTBar_3J1T.root nJ=3 nB=1 mc hlt
#cmsRun $CFGPY inputFiles_load=../fileLists/TTBar.txt maxEvents=10000 outputFile=stpol_TTBar_3J2T.root nJ=3 nB=2 mc hlt
