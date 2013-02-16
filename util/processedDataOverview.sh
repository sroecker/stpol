#!/bin/bash

for i in WD_*
do
    if [ ! -d $i ]; then continue; fi;
    INPUTDS=`cat $i/log/crab.log | grep "CMSSW.datasetpath" | cut -d' ' -f6`
    OUTPUTDS=`grep "<User Dataset Name>" $i/log/crab.log | tail -n1 | cut -f8 -d' '`
    NEVENTS=`grep "Total Events read" $i/log/crab.log | tail -n1 | cut -d' ' -f4`     
    crab -c $i -report &> /dev/null
    #if [ ! -f $i/res/lumiSummary.json ]; then crab -c $i -report &> /dev/null; fi
    lumiCalc2.py -i $i/res/lumiSummary.json -o lumi.out overview &> /dev/null
    if [ -f lumi.out ]
    then
        LUMI=`~/singletop/stpol/util/addLumis.py lumi.out`
        rm lumi.out
    fi
    if [ -f "$i.root" ]
    then
        echo "Moving output file "$i".root"
        mv "$i.root" $i"_"$LUMI"_pb.root"
    fi
    echo "| "$INPUTDS" | "$OUTPUTDS" | "$LUMI" | "$NEVENTS" |"
#    for j in WD_*
#    do
#        if [ "$i" != "$j" -a -f $i/res/lumiSummary.json -a -f $j/res/lumiSummary.json ]
#        then
#            COMP=`compareJSON.py --and $i/res/lumiSummary.json $j/res/lumiSummary.json`
#            if [ "$COMP" != "{}" ]
#            then
##                echo $COMP
#                echo "Overlap between $i and $j!"
#            fi
#        fi
#    done
    echo "---"
done
