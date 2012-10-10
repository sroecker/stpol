#!/bin/bash

STEP1OF=$1
STEP2OF='out_step2.root'
ANCODE=$CMSSW_BASE'/src/SingleTopPolarization/Analysis/python'

cmsRun $ANCODE/selection_step2_cfg.py inputFiles=file:$STEP1OF outputFile=$STEP2OF
python2.7 analysis.py --file=out_step2_trees.root --batch
