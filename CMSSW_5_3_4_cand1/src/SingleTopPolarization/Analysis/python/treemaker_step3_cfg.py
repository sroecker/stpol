import FWCore.ParameterSet.Config as cms

process = cms.Process("TREEMAKER")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
    	""
    )
)

from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.treesBJets = cms.EDAnalyzer('JetCandOwnVectorTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("bTagsTCHPtight"),
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
				cms.untracked.PSet(
					tag = cms.untracked.string("bTag"),
					expr = cms.untracked.string("bDiscriminator('trackCountingHighPurBJetTags')")
				),
			)
		),
	)
)

process.treesJets = cms.EDAnalyzer('JetCandViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
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
				cms.untracked.PSet(
					tag = cms.untracked.string("bTag"),
					expr = cms.untracked.string("bDiscriminator('trackCountingHighPurBJetTags')")
				),
			)
		),
	)
)

process.treesMu = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("goodSignalMuons"),
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
				cms.untracked.PSet(
					tag = cms.untracked.string("deltaBetaCorrRelIso"),
					expr = cms.untracked.string("userFloat('deltaBetaCorrRelIso')")
				),
			)
		),
		cms.untracked.PSet(
			collection = cms.untracked.string("goodQCDMuons"),
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
				cms.untracked.PSet(
					tag = cms.untracked.string("deltaBetaCorrRelIso"),
					expr = cms.untracked.string("userFloat('deltaBetaCorrRelIso')")
				),
			)
		),
	)
)

process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
	makeTree = cms.untracked.bool(True),
	treeName = cms.untracked.string("eventTree"),
	collections = cms.untracked.VPSet(
		cms.untracked.PSet(
			collection = cms.untracked.string("goodSignalElectrons"),
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
				cms.untracked.PSet(
					tag = cms.untracked.string("rhoCorrRelIso"),
					expr = cms.untracked.string("userFloat('rhoCorrRelIso')")
				),
			)
		),
		cms.untracked.PSet(
			collection = cms.untracked.string("goodQCDElectrons"),
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
				cms.untracked.PSet(
					tag = cms.untracked.string("rhoCorrRelIso"),
					expr = cms.untracked.string("userFloat('rhoCorrRelIso')")
				),
			)
		),
	)
)

process.TFileService = cms.Service(
    "TFileService",
    fileName = cms.string("out_step3_trees.root"),
)

process.p = cms.Path(
	process.treesJets *
	process.treesBJets *
	process.treesMu *
	process.treesEle
)
