Single top polarization analysis
=====

#SETUP

### Clone the repo

For read-only access you can use
>git clone git://github.com/HEP-KBFI/stpol.git

If you also wish to commit, you'll have to have a github account and be added to the group, then you can use
>git clone git@github.com:HEP-KBFI/stpol.git


### Make sure you have sourced cmsset

>source /cvmfs/cms.cern.ch/cmsset_default.sh

### Create the workspace

Run the following to create the CMSSW directory, link the SingleTopPolarization source code folder to it and compile everything
>. ./setup.sh

#ANALYSIS PATHWAY

The generic analysis pathway is as follows, all the relevant *.py files are in $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/:

0. *selection_step1_cfg.py* for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. *selection_step2_cfg.py* for event selection according 1 lepton, MET, N-Jet and M-tag.

For convenience, the steps have been wrapped as methods that are called from the files *step1_cfg.py* and *step2_cfg.py*.

#SYNC INPUT FILES

t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12-PU_S7_START52_V9-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FCE664EC-E79B-E111-8B06-00266CF2507C.root (1 runs, 18 lumis, 5279 events, 2261976796 bytes)

t-channel (/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM)

>/hdfs/local/stpol/sync2012/FEFF01BD-87DC-E111-BC9E-003048678F8E.root (1 runs, 40 lumis, 11789 events, 4271759218 bytes)

#DEBUGGING

Compile the code using the following command to enable LogDebug and related debugging symbols
>scram b -j8 USER_CXXFLAGS="-DEDM_ML_DEBUG"

Check for memory errors using valgrind:

>valgrind --tool=memcheck `cmsvgsupp` --leak-check=yes --show-reachable=yes --num-callers=20 --track-fds=yes cmsRun your_cfg.py >& vglog.out &

The most important memory errors are in the end of vglog.out

#RUNNING

##TTBar estimation
The goal is to select a ttbar enriched region and compare the distribution of some interesting variable to data.
>cmsRun runconfs/step2_cfg.py mc hlt mu ele nJets=3 nBTags=1 inputFiles_load=fileLists/TTBar.txt maxEvents=10000 outputFile=stpol_TTBar_3J1T.root

This will give you *stpol_TTBar_3J1T_trees.root* which contain the trees for the ttbar-enriched region.

##Sync
https://twiki.cern.ch/twiki/bin/view/CMS/SyncSingleTopLeptonJets2012
>cmsRun runconfs/step1_sync_cfg.py inputFiles=/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root outputFile=sync_step1/sync_T_t_lepIso02_newIso.root &> log1

##CRAB
To create the crab.cfg files to run over step1-data, run in the base directory
>python2.7 $CMSSW_BASE/../util/datasets.py -t your_tag -T $CMSSW_BASE/../crabs/crab_Data_step1.cfg -d S1D -o your_crab_output_dir
To create the crab.cfg files to run over step2-mc (iso/antiIso), run in the base directory
>python2.7 $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -d S2newMC -o crabs/step2_MC_Iso 
>python2.7 $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -d S2newMC -o crabs/step2_MC_antiIso 
>python2.7 $CMSSW_BASE/../util/datasets.py -t your_tag -T $CMSSW_BASE/../crabs/crab_Data_step2_Iso.cfg -d S2D -o crabs/step2_Data_Iso

###Using lumiCalc2.py
To calculate the integrated luminosity from crab jobs, do the following
>crab -c YOUR_DIR -report
>lumiCalc2.py --without-checkforupdate -i YOUR_DIR/res/lumiSummary.json overview
