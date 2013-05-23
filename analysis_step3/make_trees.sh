#!/bin/bash
timestamp=`eval date +%m_%d_%H_%M`
OFDIR=out_step3_$timestamp
FLDIR=filelist_step2_05_10
mkdir -p $OFDIR
mkdir -p $OFDIR/iso/nominal
mkdir -p $OFDIR/antiiso/nominal

$STPOL_DIR/analysis_step3/suball.sh " " $OFDIR/iso/nominal $FLDIR/iso/data/*
$STPOL_DIR/analysis_step3/suball.sh " " $OFDIR/antiiso/nominal $FLDIR/antiiso/data/*
$STPOL_DIR/analysis_step3/suball.sh "--isMC" $OFDIR/iso/nominal $FLDIR/iso/mc/*
$STPOL_DIR/analysis_step3/suball.sh "--isMC" $OFDIR/antiiso/nominal $FLDIR/antiiso/mc/*
