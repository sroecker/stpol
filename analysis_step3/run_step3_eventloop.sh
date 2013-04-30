#!/bin/bash
set -e #Abort if errors
uname -a

WD=$CMSSW_BASE/..
INFILE=$1
OUTDIR=$2
OFNAME=$SLURM_JOB_ID
if [ -z $OFNAME ]
then
    OFNAME=`python -c 'import uuid; print uuid.uuid1()'`
fi

cd $WD
source setenv.sh CMSSW_5_3_8
ls /hdfs
cd $OUTDIR
#for f in `cat $INFILE`
#do
#    edmFileUtil $f
#done
time cat $INFILE | STPOL_STEP3_OUTPUTFILE="out_step3_"$OFNAME".root" $CMSSW_BASE/bin/slc5_amd64_gcc462/Step3_EventLoop $CMSSW_BASE/../runconfs/step3_eventLoop_cfg.py
