#!/bin/bash
OFDIR=out_step3
mkdir $OFDIR
mkdir $OFDIR/iso
mkdir $OFDIR/iso/mc
mkdir $OFDIR/iso/data
mkdir $OFDIR/anti-iso
mkdir $OFDIR/anti-iso/mc
mkdir $OFDIR/anti-iso/data

STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/iso/data fileList_Step2_04_05/iso/data/*
STPOL_ISMC=false analysis_step3/suball.sh $OFDIR/anti-iso/data fileList_Step2_04_05/anti-iso/data/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/iso/mc fileList_Step2_04_05/iso/mc/*
STPOL_ISMC=true analysis_step3/suball.sh $OFDIR/anti-iso/mc fileList_Step2_04_05/anti-iso/mc/*
