#!/bin/bash

WD=/home/andres/single_top/stpol
INFILE=$1
OUTDIR=$2
OFNAME=$3
if [ -z $OFNAME ]
then
    OFNAME=`python -c 'import uuid; print uuid.uuid1()'`
fi

cd $WD
#source setenv.sh CMSSW_5_3_8
cd $WD
cd $OUTDIR

time cat $WD/$INFILE | STPOL_STEP3_OUTPUTFILE="step3_"$OFNAME".root" $CMSSW_BASE/bin/slc5_amd64_gcc462/Step3_EventLoop_unfolding_presel $CMSSW_BASE/../runconfs/step3_eventLoop_unfolding_preselection_cfg.py
