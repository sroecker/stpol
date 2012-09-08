#!/bin/bash

cmsrel CMSSW_5_3_3_patch3
cd CMSSW_5_3_3_patch3
cmsenv
cd $CMSSW_BASE/src
addpkg PhysicsTools/PatAlgos   V08-09-23      
addpkg PhysicsTools/PatUtils   V03-09-23      
addpkg CommonTools/ParticleFlow   V00-03-16
addpkg CommonTools/RecoUtils   V00-00-12                                  
addpkg CommonTools/RecoAlgos  V00-03-23        
addpkg DataFormats/ParticleFlowCandidate   V15-03-02      
addpkg DataFormats/TrackReco   V10-02-02      
addpkg DataFormats/VertexReco   V02-00-04 

##Electron ID setup
#cvs co -r V00-00-13 -d EGamma/EGammaAnalysisTools UserCode/EGamma/EGammaAnalysisTools
#cd EGamma/EGammaAnalysisTools/data
#cat download.url | xargs wget

cd $CMSSW_BASE/src
