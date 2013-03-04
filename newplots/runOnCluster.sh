#!/bin/bash

WORKDIR=/home/joosep/singletop/stpol
source ~/.bash_profile

cd $WORKDIR
source setenv.sh

cd newplots
python plots.py
