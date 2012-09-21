import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.demo = cms.EDAnalyzer('CandViewTreemakerAnalyzer',
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("goodMuons"),
			maxElems = cms.untracked.int32(1),
			variables = cms.untracked.VPSet(
				cms.untracked.PSet(
					tag = cms.untracked.string("Pt"),
					expr = cms.untracked.string("pt")
				), 
				cms.untracked.PSet(
					tag = cms.untracked.string("Eta"),
					expr = cms.untracked.string("eta")
				),
				cms.untracked.PSet(
					tag = cms.untracked.string("Phi"),
					expr = cms.untracked.string("phi")
				),
			)
		),
		cms.untracked.PSet(
			collection = cms.untracked.string("goodJets"),
			maxElems = cms.untracked.int32(2),
			variables = cms.untracked.VPSet(
				cms.untracked.PSet(
					tag = cms.untracked.string("Pt"),
					expr = cms.untracked.string("pt")
				), 
				cms.untracked.PSet(
					tag = cms.untracked.string("Eta"),
					expr = cms.untracked.string("eta")
				),
				cms.untracked.PSet(
					tag = cms.untracked.string("Phi"),
					expr = cms.untracked.string("phi")
				),
			)
		),
	)
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("trees.root"),
)

process.p = cms.Path(process.demo)
