#!/bin/bash
#mv CMSSW_5_3_4_cand1/SingleTopPolarization ./
git stash
rm -Rf CMSSW_5_3_4
export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel CMSSW_5_3_4
git reset --hard
cd CMSSW_5_3_4

cmsenv
cd $CMSSW_BASE/src

addpkg DataFormats/PatCandidates       V06-05-06-01
addpkg PhysicsTools/PatAlgos           V08-09-37
addpkg PhysicsTools/PatUtils           V03-09-26
addpkg CommonTools/RecoUtils           V00-00-12
addpkg CommonTools/RecoAlgos           V00-03-24
addpkg CommonTools/ParticleFlow        V00-03-16
addpkg RecoParticleFlow/PFProducer   V15-02-05-01
addpkg DataFormats/ParticleFlowCandidate   V15-03-04      
addpkg DataFormats/TrackReco   V10-02-02      
addpkg DataFormats/VertexReco   V02-00-04 
addpkg RecoParticleFlow/PFProducer V15-02-06


##Tags for V08-09-31 from https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_31
#addpkg DataFormats/PatCandidates       V06-05-06
#addpkg PhysicsTools/PatAlgos           V08-09-33
#cvs up -r V08-09-07-05 PhysicsTools/PatAlgos/python/patTemplate_cfg.py
#addpkg PhysicsTools/PatUtils           V03-09-26
#addpkg CommonTools/ParticleFlow        V00-03-16
#addpkg CommonTools/RecoUtils           V00-00-12
#addpkg CommonTools/RecoAlgos           V00-03-23
#addpkg DataFormats/ParticleFlowCandidate   V15-03-02      
#addpkg DataFormats/TrackReco   V10-02-02      
#addpkg DataFormats/VertexReco   V02-00-04
#addpkg RecoParticleFlow/PFProducer V15-01-11 #in order not to have missing isolation errors

cvs co -d EGamma/EGammaAnalysisTools UserCode/EGamma/EGammaAnalysisTools
cd EGamma/EGammaAnalysisTools/data
cat download.url | xargs wget
cd $CMSSW_BASE/src
cmsenv
scram b -j 24 &> scram_log
cd $CMSSW_BASE/../
