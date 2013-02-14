#!/bin/bash
for i in `find . -name 'WD_*' -type d`
do
    echo $i
    rm -f /tmp/joosep/tree_*.root
    echo "First pass"
    find $i/res -name "*.root" | parallel -n10 'hadd -f /tmp/joosep/tree_{#}.root {} > /dev/null'
    echo "Second pass"
    hadd -f ${i:5}.root /tmp/joosep/tree_*.root > /dev/null
    rm /tmp/joosep/tree_*.root
done
