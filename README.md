Single top polarization analysis
=====

SETUP
=====
0. Make sure you have sourced cmsset
1. run the following to create the CMSSW directory, link the SingleTopPOlarization source code folder to it and compile everything

>$ . ./setup.sh

2. a simple test of the moudle can be used by running 
>$ python stepMetrics.py "file:/path/to/input.root"
where input.root is an AODSIM-level input file
