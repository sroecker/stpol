#!/bin/bash
timestamp=`eval date +%m_%d`

python $CMSSW_BASE/../util/datasets.py -t stpol_step1_$timestamp -T $CMSSW_BASE/../crabs/crab_MC_step1.cfg -d S1_MC -o crabs/step1_MC_$timestamp
python $CMSSW_BASE/../util/datasets.py -t stpol_step1_$timestamp -T $CMSSW_BASE/../crabs/crab_Data_step1_glideInRemote.cfg -d S1_D -o crabs/step1_Data_$timestamp

