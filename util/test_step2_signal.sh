#!/bin/bash
IN=$CMSSW_BASE/../fileLists_Step1/T_t.txt
OFDIR=$CMSSW_BASE/../testing_step2_signal
rm -Rf $OFDIR
mkdir $OFDIR

time cmsRun $CMSSW_BASE/../runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles_load=$IN isMC=True channel=signal subChannel=T_t outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
