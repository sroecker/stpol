#!/bin/bash
timestamp=`eval date +%m_%d_%H_%M`
OFDIR=out_step3_$timestamp
FLDIR=filelist_step2_latest
mkdir -p $OFDIR/mu
mkdir -p $OFDIR/mu/iso/nominal
mkdir -p $OFDIR/mu/antiiso/nominal

$STPOL_DIR/analysis_step3/suball.sh "--mtw " $OFDIR/mu/iso/nominal $FLDIR/iso/nominal/data/*
$STPOL_DIR/analysis_step3/suball.sh "--mtw " $OFDIR/mu/antiiso/nominal $FLDIR/antiiso/nominal/data/*
$STPOL_DIR/analysis_step3/suball.sh "--mtw --isMC" $OFDIR/mu/iso/nominal $FLDIR/iso/nominal/mc/*
$STPOL_DIR/analysis_step3/suball.sh "--mtw --isMC" $OFDIR/mu/antiiso/nominal $FLDIR/antiiso/nominal/mc/*
