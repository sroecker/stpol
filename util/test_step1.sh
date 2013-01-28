#!/bin/bash
IN=/store/relval/CMSSW_5_3_6-START53_V14/RelValTTbar/GEN-SIM-RECO/v2/00000/62B0DFF3-F729-E211-9754-001A92811744.root
OFDIR=testing_step1
rm -Rf $OFDIR
mkdir $OFDIR
cmsRun runconfs/step1_newCmdLine_cfg.py inputFiles=$IN outputFile=$OFDIR/out_step1.root maxEvents=100 &> $OFDIR/log_step1.txt
echo $?
