#!/bin/bash
timestamp=`eval date +%m_%d`

mkdir $CMSSW_BASE/../crabs/$timestamp/

for SYST in "EnUp" "EnDown" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
   #mkdir $CMSSW_BASE/../crabs/$timestamp/$SYST
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso_$SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -s $SYST -d S2_MC_noQCD -o crabs/$timestamp/$SYST/
done
