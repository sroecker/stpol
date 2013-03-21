#!/bin/bash

WD=/home/joosep/singletop/stpol
OUTDIR=$1
INFILE=$2
cd $WD
source setenv.sh CMSSW_5_3_8
cd $OUTDIR
time cat $INFILE | $CMSSW_BASE/bin/slc5_amd64_gcc462/Step3_EventLoop $CMSSW_BASE/../runconfs/step3_eventLoop_cfg.py
