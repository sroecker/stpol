#!/bin/bash
IN=/store/mc/Summer12_DR53X/TToLeptons_t-channel_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/F67757FE-CEDE-E111-9330-00259073E3AE.root
OFDIR=$CMSSW_BASE/../testing_step1_signal/
echo "Running test_step1 with input $IN and output to $OFDIR"
rm -Rf $OFDIR
mkdir $OFDIR
cmsRun $CMSSW_BASE/../runconfs/step1_newCmdLine_cfg.py inputFiles=$IN outputFile=$OFDIR/out_step1.root maxEvents=1000 doSkimming=False doSlimming=False &> $OFDIR/log_step1.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
