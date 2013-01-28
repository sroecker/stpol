#!/bin/bash
IN=/store/relval/CMSSW_5_3_6-START53_V14/RelValTTbar/GEN-SIM-RECO/v2/00000/62B0DFF3-F729-E211-9754-001A92811744.root
cmsRun runconfs/step1_newCmdLine_cfg.py inputFiles=$IN outputFile=out_step1.root maxEvents=100 &> log_step1.txt
echo $?
