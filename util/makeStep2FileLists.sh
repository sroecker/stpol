#!/bin/bash

if [ -z "$1" ]
then
    echo "Usage: $0 step2_output_dir"
    exit 1
fi

for i in `find $1 -name 'WD_*' -type d`
do
    foldername=`basename $i`
    \ls -1 $i/res/*.root | $CMSSW_BASE/../util/dedupe.py | $CMSSW_BASE/../util/prependPrefix.py file: > ${foldername:3}.txt
done
