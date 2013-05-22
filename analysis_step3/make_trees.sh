#!/bin/bash
timestamp=`eval date +%m_%d_%H_%M`
OFDIR=out_step3_$timestamp
FLDIR=filelist_step2_05_10
mkdir -p $OFDIR
mkdir -p $OFDIR/iso
mkdir -p $OFDIR/antiiso

STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/iso/nominal $FLDIR/iso/data/*
STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/antiiso/nominal $FLDIR/antiiso/data/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/iso/nominal $FLDIR/iso/mc/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/antiiso/nominal $FLDIR/antiiso/mc/*
