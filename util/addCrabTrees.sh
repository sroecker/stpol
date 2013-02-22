#!/bin/bash
WD="/tmp/joosep/"${PWD##*/}
export WD
mkdir $WD
for i in `find . -name 'WD_*' -type d`
do
    echo $i
    rm -f $WD/tree_*.root
    echo "First pass"
    find $i/res -name "*.root" | parallel -n10 'hadd -f $WD/tree_{#}.root {} > /dev/null'
    echo "Second pass"
    hadd -f ${i:5}.root $WD/tree_*.root > /dev/null
    rm $WD/tree_*.root
done
