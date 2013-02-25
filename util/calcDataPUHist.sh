#!/bin/bash

DIR=~/singletop/stpol
curl -k https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/PileUp/pileup_latest.txt > $DIR/pileup_latest.txt
pileupCalc.py -i $DIR/crabs/lumis/total.json --inputLumiJSON $DIR/pileup_latest.txt --calcMode true --minBiasXsec 69400 --maxPileupBin 60 --numPileupBins 60 $DIR/data_PU.root 


