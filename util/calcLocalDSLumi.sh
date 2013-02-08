#!/bin/bash
DS=$1
~/util/das_cli.py --query="run dataset=$DS instance=cms_dbs_ph_analysis_02" --limit=0 > runs
python2.7 ~/singletop/stpol/util/getJSONbyRun.py ~/singletop/stpol/crabs/lumis/total.json runs > DS.json
rm runs
lumiCalc2.py -i DS.json overview
rm DS.json

