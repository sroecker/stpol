Single top polarization analysis
=====

SETUP
=====
0. Make sure you have sourced cmsset

>source /cvmfs/cms.cern.ch/cmsset_default.sh

1. run the following to create the CMSSW directory, link the SingleTopPolarization source code folder to it and compile everything

>. ./setup.sh

2. a simple test of the code can be run by using 

>cd $CMSSW_BASE/

>cmsenv

>cd ..

>cmsRun $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step1_cfg.py inputFiles=file:/path/to/input/file.root outputFile=out_step1.root maxEvents=100

>. .\test.sh out_step1.root

ANALYSIS PATHWAY
=====
The generic analysis pathway is as follows, all the relevant *.py files are in $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/:

0. *selection_step1_cfg.py* for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. *selection_step2_cfg.py* for event selection according 1 lepton, MET, N-Jet and M-tag.
2. *treemaker_step3_cfg.py* for converting edm pat-tuples to flat TTrees.
3. *efficiency_cfg.py* for evaluating various efficiencies stored in the patTuples by CMSSW.

SYNC INPUT FILES
=====
t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FCE664EC-E79B-E111-8B06-00266CF2507C.root (1 runs, 18 lumis, 5279 events, 2261976796 bytes)

t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FEFF01BD-87DC-E111-BC9E-003048678F8E.root (1 runs, 40 lumis, 11789 events, 4271759218 bytes)

DEBUGGING
=====
>scram b USER_CXXFLAGS=-g

>scram b -j8 USER_CXXFLAGS="-DEDM_ML_DEBUG"
