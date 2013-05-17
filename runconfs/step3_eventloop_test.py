import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventLoop_cfg import *
process.fwliteInput.maxEvents = cms.int32(20000)
process.muonCuts.requireOneMuon = cms.bool(False)
process.muonCuts.requireOneElectron = cms.bool(False)
