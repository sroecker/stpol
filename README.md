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
or by using the following script
>source setenv.sh

### Create the workspace

Run the following to create the CMSSW directory, link the SingleTopPolarization source code folder to it and compile everything
>. ./setup.sh

#ANALYSIS PATHWAY

The generic analysis pathway is as follows, all the relevant *.py files are in $CMSSW_BASE/src/SingleTopPolarization/Analysis/python/:

0. *selection_step1_cfg.py* for initial event skimming and slimming (both optional), PF2PAT sequence and object ID
1. *selection_step2_cfg.py* for generic single-top specific event selection and reconstruction according 1 lepton, MET, N-Jet and M-tag.
2. *step3_eventLoop_cfg.py* for projecting out the relevant variables from the step2 trees

For convenience, the steps have been wrapped as methods that are called from the files *runconfs/step1_newCmdLine_cfg.py* and *runconfs/step2_newCmdLine_cfg.py*.

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

##Sync
https://twiki.cern.ch/twiki/bin/view/CMS/SyncSingleTopLeptonJets2012
>cmsRun runconfs/step1_sync_cfg.py inputFiles=/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root outputFile=sync_step1/sync_T_t_lepIso02_newIso.root &> log1

##CRAB
To create the crab.cfg files to run the PAT sequences (step1)
>python $CMSSW_BASE/../util/datasets.py -t your_tag -T $CMSSW_BASE/../crabs/crab_Data_step1.cfg -d S1D -o crabs/step1_Data 

###To run the met uncertainty precalculation (step1B)
>python $CMSSW_BASE/../util/datasets.py -t stpol_step1B -T /home/joosep/singletop/stpol/crabs/crab_MC_step1B_local.cfg -d S2newMC -o crabs/step1B_MC_Mar8

To create the crab.cfg files to run over the final analysis (step2) 
>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_Iso.cfg -d S2MC -o crabs/step2_MC_Iso 

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_MC_step2_local_antiIso.cfg -d S2MC -o crabs/step2_MC_antiIso 

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_Iso -T $CMSSW_BASE/../crabs/crab_Data_step2_Iso.cfg -d S2D -o crabs/step2_Data_Iso

>python $CMSSW_BASE/../util/datasets.py -t stpol_step2_antiIso -T $CMSSW_BASE/../crabs/crab_Data_step2_antiIso.cfg -d S2D -o crabs/step2_Data_antiIso

###Using lumiCalc2.py
To calculate the integrated luminosity from crab jobs, do the following
>crab -c YOUR_DIR -report
>lumiCalc2.py --without-checkforupdate -i YOUR_DIR/res/lumiSummary.json overview

#Step2 output

The canonical step2(iso) output is currently in *fileList_Step2/*,
but note that the b-tag weight is currently not yet validated

#Step3 code
The code is an FWLite loop, which is available in *CMSSW_5_3_8/src/SingleTopPolarization/Analysis/bin/Step3_EventLoop.cpp*
and can be compiled by either setting up *CMSSW_5_3_8* using (make sure you have no uncommitted changes in your working directory)

>setup.sh

and compiling the code, or moving the code and *BuildFile.xml* to the relevant place in *CMSSW_5_3_7_patch4*.
You should try to take the loop as an example and try to implement your own analysis code based on that. 
The step3 code is steered using the python config file *runconfs/step3_eventLoop_cfg.py* where you can turn on/off basic cuts:

1. lepton
2. M_T(W)
3. nJets
4. nTags
5. top mass window

If you need more variables in the trees, you should add them to the
*process.finalVars* PSet and also in the code into the *MiscVars* class. If you are adding a large separate group of variables,
it may make more sense to create a new class for these, which can be turned on/off via the config file.
You should strive to use as strict cuts as is possible for your analysis and as few variables as is possible, in order to not
be in the same situation as earlier, when running over the full step2 trees.

For batch running, the scripts in *analysis_step3* may be useful, in particular

>analysis_step3/run_step3_eventloop.sh input_files.txt /path/to/output_directory
