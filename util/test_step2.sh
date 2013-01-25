#!/bin/bash
cmsRun runconfs/step2_newCmdLine_cfg.py inputFiles_load=fileLists/SingleMu1.txt isMC=False outputFile=out.root maxEvents=10000
cmsRun runconfs/step2_newCmdLine_cfg.py inputFiles_load=fileLists/T_t.txt channel=signal subChannel=T_t outputFile=out.root maxEvents=10000
