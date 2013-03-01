#!/bin/bash
IN=`\ls -1 $CMSSW_BASE/../testing_step1/out*.root`
OFDIR=$CMSSW_BASE/../testing_step2
rm -Rf $OFDIR
mkdir $OFDIR

cmsRun $CMSSW_BASE/../runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles=file:$IN isMC=True channel=background subChannel=TTbar outputFile=$OFDIR/out.root &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
