#!/bin/bash
IN=$CMSSW_BASE/../testing_step1/out_step1_numEvent100_Skim.root
OFDIR=$CMSSW_BASE/../testing_step1B
rm -Rf $OFDIR
mkdir $OFDIR
cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/metUncertaintyStep_cfg.py inputFiles=file:$IN outputFile=$OFDIR/out_step1B.root maxEvents=100 &> $OFDIR/log_step1B.txt
echo $?
