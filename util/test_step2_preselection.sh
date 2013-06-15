#!/bin/bash
echo "Running step2 test on signal"
IN=file:~/single_top/stpol/testing_step1_signal/out_step1_numEvent1000_noSkim_noSlim.root
OFDIR=$CMSSW_BASE/../testing_step2_presel
#rm -Rf $OFDIR
mkdir $OFDIR

time cmsRun $CMSSW_BASE/../runconfs/step2_newCmdLine_preSelection_cfg.py doDebug=True inputFiles=$IN subChannel=T_t outputFile=$OFDIR/out.root maxEvents=10000 &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
