#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for var in "$@"
do
    root2hdf5 -f --script=$DIR/isRequired.py $var
    HFILE=${var%.*}".h5"
    python2.7 $DIR/mergeTables.py ${var%.*}".h5"
#    rm $HFILE
done
