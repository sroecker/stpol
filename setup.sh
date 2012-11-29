#!/bin/bash
#mv CMSSW_5_3_4_cand1/SingleTopPolarization ./
#Tags for https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATReleaseNotes52X#V08_09_43
CMSVERSION=CMSSW_5_3_5
git stash
rm -Rf $CMSVERSION
export SCRAM_ARCH=slc5_amd64_gcc462
cmsrel $CMSVERSION 
git reset --hard
cd $CMSVERSION 

cmsenv
cd $CMSSW_BASE/src

addpkg DataFormats/PatCandidates            V06-05-06-03
addpkg PhysicsTools/PatAlgos                V08-09-43
addpkg PhysicsTools/PatUtils                V03-09-26
addpkg CommonTools/RecoUtils                V00-00-12
addpkg CommonTools/RecoAlgos                V00-03-24
addpkg CommonTools/ParticleFlow             V00-03-16
addpkg RecoParticleFlow/PFProducer          V15-02-05-01
addpkg DataFormats/ParticleFlowCandidate    V15-03-04      
addpkg DataFormats/TrackReco                V10-02-02      
addpkg DataFormats/VertexReco               V02-00-04 
addpkg RecoParticleFlow/PFProducer          V15-02-06
addpkg RecoLuminosity/LumiDB                V04-01-09
cvs co -r V00-00-31 -d EGamma/EGammaAnalysisTools UserCode/EGamma/EGammaAnalysisTools
cd EGamma/EGammaAnalysisTools/data
cat download.url | xargs wget
cd $CMSSW_BASE/src

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFilters#EB_or_EE_Xtals_with_large_laser
cvs co RecoMET/METFilters/

#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PileupJetID
cvs co -r V00-02-10 -d CMGTools/External UserCode/CMG/CMGTools/External

cmsenv
scram b -j 24 &> scram_log
cd $CMSSW_BASE/../
