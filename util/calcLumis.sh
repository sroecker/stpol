#!/bin/bash

filter() {
    echo "----------------------------------------"
    echo "Run range "$2"-"$3
    wget --no-check-certificate $1 -O in.txt &> /dev/null
    lumiCalc2.py --begin $2 --end $3 -i in.txt overview > tmp_out
    grep -A2 "Recorded(/" tmp_out | grep -v "-"
    rm in.txt
    rm tmp_out
    echo "----------------------------------------"
    echo ""
}

echo "Run2012A-13Jul2012"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt' 190456 193621

echo "Run2012A-recover-06Aug2012"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt' 190782 190949 

echo "Run2012B-13Jul2012"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt' 193833 196531 

echo "Run2012C-ReReco"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt' 198022 198913

echo "Run2012C-PromptReco-v2"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Prompt/Cert_190456-203002_8TeV_PromptReco_Collisions12_JSON_v2.txt' 198934 203746

echo "Run2012C-EcalRecover_11Dec2012"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_201191-201191_8TeV_11Dec2012ReReco-recover_Collisions12_JSON.txt' 201191 201191

echo "Run2012D-PromptReco-v1"
filter 'https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Prompt/Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt' 203768 208686

