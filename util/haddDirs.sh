#!/bin/bash

files=`find $1 -name "*.root" -exec dirname {} \; | sort | uniq`

for f in $files
do
    echo hadd $f.root $f/out*.root
done
