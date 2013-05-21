import FWCore.ParameterSet.Config as cms
from runconfs.step3_eventLoop_cfg import *
process.muonCuts.requireOneMuon = cms.bool(True)
process.muonCuts.requireOneElectron = cms.bool(False)
process.HLTmu.cutOnHLT = cms.bool(True)
