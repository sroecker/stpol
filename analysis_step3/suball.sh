#!/bin/bash

OFDIR=$1
INFILES="${*:2}"
if [ -z "$OFDIR" ]
then
    echo "Usage: $0 OFDIR INFILES"
    exit 1
fi
WD=$CMSSW_BASE/..
SUBSCRIPT=$WD/analysis_step3/slurm_sub_step3.sh
for infile in $INFILES
do
    echo $infile
    fullpath=$(readlink -f $infile)
    filename=$(basename $infile)
    channel="${filename%.*}"
    echo $channel
    $SUBSCRIPT $fullpath $OFDIR/$channel 
done
