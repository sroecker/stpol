#!/bin/bash

INFILE=$1
JOBNAME=$2
if [ -z "$INFILE" ]; then echo "$0 INFILE JOBNAME"; fi
if [ -z "$JOBNAME" ]; then echo "$0 INFILE JOBNAME"; fi
WD=$CMSSW_BASE/../step3_out
OFDIR=$WD/$JOBNAME
#rm -Rf $WD/$JOBNAME
mkdir $OFDIR

cd $WD/$JOBNAME
split $INFILE -l 10 -d
for file in x*
do
    $CMSSW_BASE/../misc/run_step3_eventloop.sh $OFDIR $INFILE & 
done
