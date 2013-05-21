import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventLoop_cfg import *

process.fwliteInput.maxEvents = cms.int32(-1)

process.muonCuts.requireOneMuon = False
process.muonCuts.doVetoLeptonCut = False

process.eleCuts.requireOneElectron = False
process.eleCuts.doVetoLeptonCut = False

process.jetCuts.cutOnNJets = False
process.bTagCuts.cutOnNTags = False

process.mtMuCuts.doMTCut = False

process.HLTmu.saveHLTVars = True
process.HLTmu.doCutOnHLT = False

process.HLTele.saveHLTVars = True
process.HLTele.doCutOnHLT = False
