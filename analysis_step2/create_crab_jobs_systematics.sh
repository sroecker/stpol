#!/bin/bash
timestamp=`eval date +%m_%d`

for SYST in "EnUp" "EnDown" "ResUp" "ResDown"
do
   mkdir $CMSSW_BASE/../crabs/$SYST
	python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso_$SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -s $SYST -d S2_MC -o crabs/$SYST/step2_MC_Iso_$timestamp
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso_$SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -s $SYST -d S2_MC -o crabs/$SYST/step2_MC_antiIso_$timestamp

done
