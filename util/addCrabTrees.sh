#!/bin/bash
for i in `find . -name 'WD_*' -type d`
WD=/tmp/joosep/${PWD##*/}
mkdir $WD
rm -f $WD/*
do
    echo $i
    rm $WD/*.root
    echo "First pass"
    find $i/res -name "*.root" | parallel -n10 'hadd -f $WD/tree_{#}.root {} > /dev/null'
    echo "Second pass"
    hadd -f ${i:5}.root $WD/tree_*.root > /dev/null
    rm $WD/tree_*.root
done
