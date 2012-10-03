#!/bin/bash

ANCODE=$CMSSW_BASE'/src/SingleTopPolarization/Analysis/python'

F1=/hdfs/local/stpol/sync2012/FE70A139-7B8E-E111-9C50-002618943856.root
F2=/hdfs/local/stpol/sync2012/FCE664EC-E79B-E111-8B06-00266CF2507C.root

cmsRun $ANCODE/selection_step1_cfg.py inputFiles=file:$F1 outputFile=sync_step1/sync_Tbar_t.root &> sync_Tbar_t_step1.log &
cmsRun $ANCODE/selection_step1_cfg.py inputFiles=file:$F2 outputFile=sync_step1/sync_T_t.root &> sync_T_t_step1.log &
