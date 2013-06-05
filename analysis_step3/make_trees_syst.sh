#!/bin/bash
timestamp=`eval date +%m_%d`
OFDIR=out_step3_$timestamp
FILELIST_SYST=filelist_step2_systematics_28_05
FILELIST=filelist_step2_latest

mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/antiiso
mkdir $OFDIR/iso/SYST

for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/iso/$SYST
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --doFinal --isWplusJets" $OFDIR/iso/$SYST $FILELIST_SYST/Iso/$SYST/W*Jets_exclusive*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --doFinal" $OFDIR/iso/$SYST $FILELIST_SYST/Iso/$SYST/[A-V]*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --doFinal" $OFDIR/iso/$SYST $FILELIST_SYST/Iso/$SYST/WW*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --doFinal" $OFDIR/iso/$SYST $FILELIST_SYST/Iso/$SYST/Z*

    #Just in case, to avoid overload...    
    sleep 100
done


for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
    mkdir $OFDIR/antiiso/$SYST
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --isAntiIso --doFinal --isWplusJets" $OFDIR/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/W*Jets_exclusive*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --isAntiIso --doFinal" $OFDIR/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/[A-V]*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --isAntiIso --doFinal" $OFDIR/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/WW*
    $STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --isAntiIso --doFinal" $OFDIR/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/Z*

    #Just in case, to avoid overload...    
    sleep 100
done

$STPOL_DIR/analysis_step3/suball_syst.sh "--doFinal" $OFDIR/iso/Nominal $FILELIST/iso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "--isAntiIso --doFinal" $OFDIR/antiiso/Nominal $FILELIST/antiiso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "--isMC --doFinal" $OFDIR/iso/SYST $FILELIST_SYST/Iso/SYST/*
