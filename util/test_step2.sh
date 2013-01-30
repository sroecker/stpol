#!/bin/bash
IN=`\ls -1 testing_step1/out*.root`
OFDIR=testing_step2
rm -Rf $OFDIR
mkdir $OFDIR

cmsRun runconfs/step2_newCmdLine_cfg.py inputFiles=file:$IN isMC=True channel=background subChannel=TTbar outputFile=$OFDIR/out.root &> $OFDIR/log_step2.txt
echo $?
