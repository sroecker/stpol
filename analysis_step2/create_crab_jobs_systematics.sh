#!/bin/bash
timestamp=`eval date +%m_%d`
#timestamp=31_05
mkdir $STPOL_DIR/crabs/out_step2/$timestamp/
mkdir $STPOL_DIR/crabs/out_step2/$timestamp/iso
mkdir $STPOL_DIR/crabs/out_step2/$timestamp/antiiso

python $STPOL_DIR/util/datasets.py -t stpol_step2_Iso_SYST_$timestamp -T $STPOL_DIR/crabs/crab_MC_step2_local_Iso_copydata.cfg -s SYST -d S2_MC_syst -o crabs/out_step2/$timestamp/iso/Syst

python $STPOL_DIR/util/datasets.py -t stpol_step2_presel_$timestamp -T $STPOL_DIR/crabs/crab_MC_step2_local_presel_copydata.cfg -s Presel -d S2_SIG -o crabs/out_step2/$timestamp/presel

for SYST in "Nominal" "EnUp" "EnDown" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso_$SYST_$timestamp -T $STPOL_DIR/crabs/crab_MC_step2_local_Iso_copydata.cfg -s $SYST -d S2_MC_noQCD -o crabs/out_step2/$timestamp/iso/$SYST/
   python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso_$SYST_$timestamp -T $STPOL_DIR/crabs/crab_MC_step2_local_antiIso_copydata.cfg -s $SYST -d S2_MC_noQCD -o crabs/out_step2/$timestamp/antiiso/$SYST/
done
