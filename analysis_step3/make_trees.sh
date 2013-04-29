#!/bin/bash
OFDIR=out_step3_04_29_2
FLDIR=filelist_step2_04_25
mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/iso/mc
mkdir $OFDIR/iso/data
mkdir $OFDIR/anti-iso
mkdir $OFDIR/anti-iso/mc
mkdir $OFDIR/anti-iso/data

STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/iso/data $FLDIR/iso/data/*
STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/anti-iso/data $FLDIR/anti-iso/data/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/iso/mc $FLDIR/iso/mc/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/anti-iso/mc $FLDIR/anti-iso/mc/*
