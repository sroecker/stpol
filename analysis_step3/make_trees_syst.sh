#!/bin/bash
timestamp=`eval date +%m_%d`
OFDIR=out_step3_$timestamp
FILELIST_SYST=filelist_step2_systematics_28_05
FILELIST=filelist_step2_latest

mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/antiiso
mkdir $OFDIR/iso/SYST


$STPOL_DIR/analysis_step3/suball_syst.sh "" $OFDIR/iso/Nominal $FILELIST/iso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "--isAntiIso" $OFDIR/antiiso/Nominal $FILELIST/antiiso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "" $OFDIR/iso/SYST $FILELIST_SYST/Iso/SYST/*

#Just in case, to avoid overload...    
sleep 300

for SYST in "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/iso/$SYST
    $STPOL_DIR/analysis_step3/suball_syst.sh "" $OFDIR/iso/$SYST $FILELIST_SYST/Iso/$SYST/*

    #Just in case, to avoid overload...    
    sleep 300
done


for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/antiiso/$SYST
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isAntiIso" $OFDIR/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/*

    #Just in case, to avoid overload...    
    sleep 300
done
