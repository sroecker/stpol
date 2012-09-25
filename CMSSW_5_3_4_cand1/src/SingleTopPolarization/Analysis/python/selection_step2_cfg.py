import FWCore.ParameterSet.Config as cms

process = cms.Process("STPOL2")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(""
    )
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('output_step2.root'),
     SelectEvents = cms.untracked.PSet(
         SelectEvents = cms.vstring('p')
     ),
    outputCommands = cms.untracked.vstring('keep *')
)
process.outpath = cms.EndPath(process.out)

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

process.looseMuVeto = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoMuons"),
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(2),
)

process.nJets = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodJets"),
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(2),
)

process.mBTags = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("bTagsTCHPtight"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

process.p = cms.Path(
    process.oneIsoMu * 
    process.looseMuVeto * 
    process.nJets *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.mBTags
)
