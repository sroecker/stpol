#!/bin/bash
echo "Running step2 test on data"
IN=file:/hdfs/cms/store/user/joosep/SingleMu/step1_Data_Feb6/4ad4eefaf926ac722f9a48104acbb5cc/output_Skim_1_1_wWD.root
OFDIR=$CMSSW_BASE/../testing_step2_data
rm -Rf $OFDIR
mkdir $OFDIR

time cmsRun $CMSSW_BASE/../runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles=$IN isMC=False outputFile=$OFDIR/out.root maxEvents=5000 &> $OFDIR/log.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    grep "Exception" -A10 $OFDIR/log*.txt
fi
grep "CPU/real" $OFDIR/log*.txt
