#!/bin/bash

INDIR=$1
if [ -z "$INDIR" ]; then echo "Usage: $0 INDIR"; exit 1; fi

for d in $INDIR/*
do
    INFILES=`find $d -name "*.root"`
    hadd $d".root" $INFILES 
done
