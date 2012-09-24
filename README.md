Single top polarization analysis
=====

SETUP
=====
0. Make sure you have sourced cmsset
1. run the following to create the CMSSW directory, link the SingleTopPOlarization source code folder to it and compile everything

>. ./setup.sh

2. a simple test of the module can be used by running 

>python $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/stepMetrics.py file:/path/to/input.root

ANALYSIS PATHWAY
=====
The generic analysis pathway is as follows:

0. $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step1_cfg.py for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step2_cfg.py for event selection according 1 lepton, MET, N-Jet and M-tag.
2. $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/treemaker_step3_cfg.py for converting edm pat-tuples to flat TTrees.