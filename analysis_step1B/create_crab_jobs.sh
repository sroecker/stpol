#!/bin/bash
timestamp=`eval date +%m_%d`

python $CMSSW_BASE/../util/datasets.py -t stpol_step1_$timestamp -T $CMSSW_BASE/../crabs/crab_MC_step1B_local.cfg -d S1B_MC -o crabs/step1B_MC_$timestamp

