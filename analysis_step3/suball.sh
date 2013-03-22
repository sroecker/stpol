#!/bin/bash

OFDIR=$1
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 OFDIR"
    exit 1
fi
WD=$CMSSW_BASE/..
for infile in $@
do
    fullpath=$(readlink -f $infile)
    filename=$(basename $infile)
    channel="${filename%.*}"
    $WD/analysis_step3/slurm_sub_step3.sh $fullpath $OFDIR/$channel
done
