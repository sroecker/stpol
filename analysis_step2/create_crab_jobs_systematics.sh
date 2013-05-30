#!/bin/bash
timestamp=`eval date +%m_%d`
#timestamp=28_05
mkdir $CMSSW_BASE/../crabs/out_step2/$timestamp/
mkdir $CMSSW_BASE/../crabs/out_step2/$timestamp/iso
mkdir $CMSSW_BASE/../crabs/out_step2/$timestamp/antiiso

#python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -s Nominal -d S2_MC_syst -o crabs/out_step2/$timestamp/iso/Syst
#python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso_SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -s SYST -d S2_SYS -o crabs/out_step2/$timestamp/SYST

for SYST in "Nominal" "EnUp" "EnDown" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso_$SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -s $SYST -d S2_MC_noQCD -o crabs/out_step2/$timestamp/iso/$SYST/
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso_$SYST -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -s $SYST -d S2_MC_noQCD -o crabs/out_step2/$timestamp/antiiso/$SYST/
done
