import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.eventCounting import *

process = cms.Process("STPOLSEL2")
countProcessed(process)

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(""
    )
)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)


process.bTagsTCHPtight = cms.EDFilter(
	"CandViewSelector",
	src = cms.InputTag("goodJets"),
	cut = cms.string('bDiscriminator("trackCountingHighPurBJetTags") > 3.41')
)

process.bTagsCSVmedium = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag("goodJets"),
    cut = cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.679')
)

process.bTagsCSVtight = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag("bTagsCSVmedium"),
    cut = cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.898')
)

process.oneIsoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodSignalMuons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

process.oneIsoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodSignalElectrons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#in mu path we must have 1 loose muon (== THE isolated muon)
process.looseMuVetoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoMuons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#In Muon path we must have 0 loose electrons
process.looseEleVetoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoElectrons"),
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(0),
)

#In Electron path we must have 1 loose electron (== the isolated electron)
process.looseEleVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoElectrons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#In Electron path we must have 0 loose muons
process.looseMuVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoMuons"),
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(0),
)

#Require exactly N jets
process.nJets = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodJets"),
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(2),
)

#Require exactly M bTags of the given type
process.mBTags = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("bTagsTCHPtight"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

process.muonPathPreCount = cms.EDProducer("EventCountProducer")
process.muPath = cms.Path(
    process.muonPathPreCount *
    process.oneIsoMu * 
    process.looseMuVetoMu * 
    process.looseEleVetoMu * 
    process.nJets *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.mBTags
)
countAfter(process, process.muPath, ["oneIsoMu", "looseMuVetoMu", "looseEleVetoMu", "nJets", "mBTags"])

process.elePath = cms.Path(
    process.muonPathPreCount *
    process.oneIsoEle * 
    process.looseEleVetoEle * 
    process.looseMuVetoEle * 
    process.nJets *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.mBTags
)
countAfter(process, process.elePath, ["oneIsoEle", "looseEleVetoEle", "looseMuVetoEle", "nJets", "mBTags"])


#-----------------------------------------------
# Outpath
#-----------------------------------------------

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('out_step2.root'),
     SelectEvents = cms.untracked.PSet(
         SelectEvents = cms.vstring(['muPath', 'elePath'])
     ),
    outputCommands = cms.untracked.vstring('keep *')
)
process.outpath = cms.EndPath(process.out)
