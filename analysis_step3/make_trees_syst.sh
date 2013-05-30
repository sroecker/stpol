#!/bin/bash
timestamp=`eval date +%m_%d`
OFDIR=out_step3_$timestamp
FILELIST=filelist_step2_systematics_28_05

mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/antiiso

for SYST in "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/iso/$SYST
    analysis_step3/suball_syst.sh "" $OFDIR/iso/$SYST $FILELIST/Iso/$SYST/*

    #Just in case, to avoid overload...    
    sleep 300
done


for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/antiiso/$SYST
    analysis_step3/suball_syst.sh "--isAntiIso" $OFDIR/antiiso/$SYST $FILELIST/antiIso/$SYST/*

    sleep 300
done
