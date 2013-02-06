#!/bin/bash

for i in WD_*
do
    echo $i":"`grep "<User Dataset Name>" $i/log/crab.log | tail -n1 | cut -f8 -d' '`
    if [ ! -f $i/res/lumiSummary.json ]; then crab -c $i -report &> /dev/null; fi
    lumiCalc2.py -i $i/res/lumiSummary.json overview | grep -A3 "Total" | grep "|" | cut -d'|' -f5 | xargs
done
