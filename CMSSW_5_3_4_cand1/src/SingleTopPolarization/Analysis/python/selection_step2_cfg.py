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

process.bTagsTCHPT = cms.EDFilter(
	"CandViewSelector",
	src = cms.InputTag("goodJets"),
	#cut = cms.string("pt > 20")
	cut = cms.string('bDiscriminator("default") > 0.9')
	#ptMin = cms.double(20)
)

process.p = cms.Path(process.bTagsTCHPT)
