#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
root2hdf5 --script=$DIR/isRequired.py $1
