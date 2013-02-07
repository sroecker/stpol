#!/bin/bash

for i in WD_*
do
    echo $i
    echo "Input DS:"`cat $i/log/crab.log | grep "CMSSW.datasetpath" | cut -d' ' -f6`
    echo "Output DS:"`grep "<User Dataset Name>" $i/log/crab.log | tail -n1 | cut -f8 -d' '`
    if [ ! -f $i/res/lumiSummary.json ]; then crab -c $i -report &> /dev/null; fi
    lumiCalc2.py -i $i/res/lumiSummary.json overview | grep -A3 "Total" | grep "|" | cut -d'|' -f5 | xargs
    for j in WD_*
    do
        if [ "$i" != "$j" ]
        then
            COMP=`compareJSON.py --and $i/res/lumiSummary.json $j/res/lumiSummary.json`
            if [ "$COMP" != "{}" ]
            then
#                echo $COMP
                echo "Overlap between $i and $j!"
            fi
        fi
    done
    echo "---"
done
