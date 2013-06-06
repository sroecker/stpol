#!/bin/bash
timestamp=`eval date +%m_%d_%H`
OFDIR=out_step3_$timestamp
FILELIST_SYST=filelist_step2_systematics_28_05
FILELIST=filelist_step2_latest

mkdir -p $OFDIR/mu
mkdir -p $OFDIR/mu/iso
mkdir -p $OFDIR/mu/antiiso
mkdir -p $OFDIR/mu/iso/SYST

mkdir -p $OFDIR/ele
mkdir -p $OFDIR/ele/iso
mkdir -p $OFDIR/ele/antiiso
mkdir -p $OFDIR/ele/iso/SYST

for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
  mkdir $OFDIR/mu/iso/$SYST
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal --isWplusJets" $OFDIR/mu/iso/$SYST $FILELIST_SYST/Iso/$SYST/W*Jets_exclusive*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal" $OFDIR/mu/iso/$SYST $FILELIST_SYST/Iso/$SYST/[A-V]*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal" $OFDIR/mu/iso/$SYST $FILELIST_SYST/Iso/$SYST/WW*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal" $OFDIR/mu/iso/$SYST $FILELIST_SYST/Iso/$SYST/WZ*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal" $OFDIR/mu/iso/$SYST $FILELIST_SYST/Iso/$SYST/Z*
  
  mkdir $OFDIR/ele/iso/$SYST
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal --isWplusJets" $OFDIR/ele/iso/$SYST $FILELIST_SYST/Iso/$SYST/W*Jets_exclusive*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal" $OFDIR/ele/iso/$SYST $FILELIST_SYST/Iso/$SYST/[A-V]*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal" $OFDIR/ele/iso/$SYST $FILELIST_SYST/Iso/$SYST/WW*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal" $OFDIR/ele/iso/$SYST $FILELIST_SYST/Iso/$SYST/WZ*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal" $OFDIR/ele/iso/$SYST $FILELIST_SYST/Iso/$SYST/Z*  
  
  #Just in case, to avoid overload...    
  sleep 300
done


for SYST in "EnUp" "EnDown" "Nominal" "ResUp" "ResDown" "UnclusteredEnUp" "UnclusteredEnDown"
do
  mkdir $OFDIR/mu/antiiso/$SYST
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --isAntiIso --doFinal --isWplusJets" $OFDIR/mu/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/W*Jets_exclusive*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --isAntiIso --doFinal" $OFDIR/mu/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/[A-V]*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --isAntiIso --doFinal" $OFDIR/mu/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/WW*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --isAntiIso --doFinal" $OFDIR/mu/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/WZ*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --isAntiIso --doFinal" $OFDIR/mu/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/Z*
  
  mkdir $OFDIR/ele/antiiso/$SYST
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --isAntiIso --doFinal --isWplusJets" $OFDIR/ele/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/W*Jets_exclusive*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --isAntiIso --doFinal" $OFDIR/ele/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/[A-V]*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --isAntiIso --doFinal" $OFDIR/ele/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/WW*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --isAntiIso --doFinal" $OFDIR/ele/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/WZ*
  $STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --isAntiIso --doFinal" $OFDIR/ele/antiiso/$SYST $FILELIST_SYST/antiIso/$SYST/Z*
  
  #Just in case, to avoid overload...    
  sleep 300
done

$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --doFinal" $OFDIR/iso/Nominal $FILELIST/mu/iso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isAntiIso --doFinal" $OFDIR/antiiso/Nominal $FILELIST/mu/antiiso/nominal/data/SingleMu*
$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=mu --isMC --doFinal" $OFDIR/iso/SYST $FILELIST_SYST/mu/Iso/SYST/*

$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --doFinal" $OFDIR/iso/Nominal $FILELIST/ele/iso/nominal/data/SingleEle*
$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isAntiIso --doFinal" $OFDIR/antiiso/Nominal $FILELIST/ele/antiiso/nominal/data/SingleEle*
$STPOL_DIR/analysis_step3/suball_syst.sh "--lepton=ele --isMC --doFinal" $OFDIR/iso/SYST $FILELIST_SYST/ele/Iso/SYST/*