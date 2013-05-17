#!/bin/bash

IN=`find $STPOL_DIR/testing_step1 -name "out*.root"`
OFDIR="$STPOL_DIR"/testing_step2

echo "Runnin step2 test on "$INFILE" with output to "$OFDIR
if [ -d "$OFDIR" ]; then
    echo "Removing "$OFDIR 
    rm -Rf "$OFDIR"
fi

mkdir $OFDIR

cmsRun $CMSSW_BASE/../runconfs/step2_newCmdLine_cfg.py doDebug=True inputFiles=file:$IN isMC=True channel=background subChannel=TTbar outputFile=$OFDIR/out.root &> $OFDIR/log_step2.txt
EX=$?
echo "Exit code:"$EX 
if [ "$EX" -ne 0 ]
then
    tail -n 50 $OFDIR/log*.txt
fi
