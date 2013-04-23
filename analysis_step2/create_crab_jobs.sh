#!/bin/bash
timestamp=`eval date +%m_%d`"_"$TAG

python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -d S2_MC -o crabs/step2_MC_Iso_$timestamp
python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_Data_step2_Iso.cfg -d S2_D -o crabs/step2_Data_Iso_$timestamp

python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -d S2_MC -o crabs/step2_MC_antiIso_$timestamp
python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_Data_step2_antiIso.cfg -d S2_D -o crabs/step2_Data_antiIso_$timestamp

