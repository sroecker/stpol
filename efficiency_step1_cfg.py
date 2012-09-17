import FWCore.ParameterSet.Config as cms

process = cms.Process("efficiencyStep1")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing('analysis')
options.parseArguments()

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(options.inputFiles)
)

process.efficiencyStep1Analyzer = cms.EDAnalyzer('EfficiencyAnalyzer'
, histogrammableCounters = cms.untracked.vstring(["singleTopPathStep1Ele", "singleTopPathStep1Mu", "totalEventCount"])
, singleTopPathStep1Ele = cms.untracked.vstring(["singleTopPathStep1ElePreCount", "singleTopPathStep1ElePostCount"])
, singleTopPathStep1Mu = cms.untracked.vstring(["singleTopPathStep1MuPreCount", "singleTopPathStep1MuPostCount"])
, totalEventCount = cms.untracked.vstring(["totalProcessedEventCount"])
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string(options.outputFile),
)



process.p = cms.Path(process.efficiencyStep1Analyzer)
