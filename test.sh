#!/bin/bash

STEP1OF='out_step1_noSkim.root'
STEP2OF='out_step2.root'
ANCODE=$CMSSW_BASE'/src/SingleTopPolarization/Analysis/python'

cmsRun $ANCODE/selection_step2_cfg.py inputFiles=file:$STEP1OF outputFile=$STEP2OF
cmsRun $ANCODE/efficiency_cfg.py inputFiles=file:$STEP2OF
cmsRun $ANCODE/treemaker_step3_cfg.py inputFiles=file:$STEP2OF