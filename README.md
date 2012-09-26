Single top polarization analysis
=====

SETUP
=====
0. Make sure you have sourced cmsset
1. run the following to create the CMSSW directory, link the SingleTopPolarization source code folder to it and compile everything

>. ./setup.sh

2. a simple test of the code can be run by using 

>cd $CMSSW_BASE/

>cmsenv

>cd ..

>cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step1_cfg.py inputFile=file:/path/to/input/file.root outputFile=out_step1.root maxEvents=100

>. .\test.sh out_step1.root

ANALYSIS PATHWAY
=====
The generic analysis pathway is as follows, all the relevant *.py files are in $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/:

0. selection_step1_cfg.py for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. selection_step2_cfg.py for event selection according 1 lepton, MET, N-Jet and M-tag.
2. treemaker_step3_cfg.py for converting edm pat-tuples to flat TTrees.
3. efficiency_cfg.py for evaluating various efficiencies stored in the patTuples by CMSSW.