#!/bin/bash

for f in `find $1 -maxdepth 1 -name "*.root"`
do
    filename=$(basename "$f")
    for fi in `find $2 -maxdepth 1 -name "$filename"`
    do
        hadd $filename $f $fi
    done
done

