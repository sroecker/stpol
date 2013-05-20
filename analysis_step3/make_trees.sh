#!/bin/bash
timestamp=`eval date +%m_%d_%H_%M`
OFDIR=out_step3_$timestamp
FLDIR=filelist_step2_latest
mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/iso/mc
mkdir $OFDIR/iso/data
mkdir $OFDIR/anti-iso
mkdir $OFDIR/anti-iso/mc
mkdir $OFDIR/anti-iso/data

STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/iso/data $FLDIR/iso/data/*
STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/anti-iso/data $FLDIR/antiiso/data/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/iso/mc $FLDIR/iso/mc/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/anti-iso/mc $FLDIR/antiiso/mc/*
