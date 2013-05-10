python plots.py -n 5 -p 100 --doFinalSel --doReweight &> log1 &
python plots.py -n 5 -p 100 --doMET --doReweight &> log2 &
python plots.py -n 5 -p 100 --doNJets --doReweight &> log3 &
python plots.py -n 5 -p 100 --doNBTags --doReweight &> log4 &
python plots.py -n 5 -p 100 --doTopMass --doReweight &> log5 &
python plots.py -n 5 -p 100 --doTTbarControl --doReweight &> log6 &
python plots.py -n 5 -p 100 --doBWeightControl --doReweight &> log7 &
python plots.py -n 5 -p 100 --doWJetsControl --doReweight &> log8 &
