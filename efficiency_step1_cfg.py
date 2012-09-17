import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/home/joosep/singletop/stpol/patTuple.root'
    )
)

process.demo = cms.EDAnalyzer('EfficiencyAnalyzer'
, histogrammableCounters = cms.untracked.vstring(["singleTopPathStep1Ele", "singleTopPathStep1Mu", "totalEventCount"])
, singleTopPathStep1Ele = cms.untracked.vstring(["singleTopPathStep1ElePreCount", "singleTopPathStep1ElePostCount"])
, singleTopPathStep1Mu = cms.untracked.vstring(["singleTopPathStep1MuPreCount", "singleTopPathStep1MuPostCount"])
, totalEventCount = cms.untracked.vstring(["totalProcessedEventCount"])
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("histo.root"),
)



process.p = cms.Path(process.demo)
