#!/bin/bash

export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel CMSSW_5_3_3_patch3
cd CMSSW_5_3_3_patch3

cmsenv
cd $CMSSW_BASE/src

#Tags for V08-09-31 from https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_31
addpkg DataFormats/PatCandidates       V06-05-06
addpkg PhysicsTools/PatAlgos           V08-09-31
#cvs up -r V08-09-07-05 PhysicsTools/PatAlgos/python/patTemplate_cfg.py
#addpkg PhysicsTools/PatUtils           V03-09-26
#addpkg CommonTools/ParticleFlow        V00-03-16
#addpkg CommonTools/RecoUtils           V00-00-12
#addpkg CommonTools/RecoAlgos           V00-03-23
#addpkg DataFormats/ParticleFlowCandidate   V15-03-02      
#addpkg DataFormats/TrackReco   V10-02-02      
#addpkg DataFormats/VertexReco   V02-00-04 

cd $CMSSW_BASE/src
scram b -j 8
cmsenv
cd $CMSSW_BASE/../
