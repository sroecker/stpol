#!/bin/bash

OFDIR=$1
INFILES="${*:2}"
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 OFDIR INFILES"
    exit 1
fi
WD=$CMSSW_BASE/..
for infile in $INFILES
do
    fullpath=$(readlink -f $infile)
    filename=$(basename $infile)
    channel="${filename%.*}"
    $WD/analysis_step3/slurm_sub_step3.sh $fullpath $OFDIR/$channel 
done
