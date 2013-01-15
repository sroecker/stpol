import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations=cms.untracked.vstring(
                                              'cout',
                    ),
       cout=cms.untracked.PSet(
        threshold=cms.untracked.string('DEBUG')
        ),
)
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring("patTuple_PF2PAT.root"
#        'file:/home/joosep/singletop/stpol/patTuple_slim_numEvent100.root'
#        'file:/hdfs/local/stpol/joosep/FEFF01BD-87DC-E111-BC9E-003048678F8E.root'
    )
)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

#process.simpleAnalyzer = cms.EDAnalyzer(
#	'SimpleMuonAnalyzer',
#	interestingCollections = cms.untracked.VInputTag(["muonsWithID", "shiftedMuonsWithIDenDown"])
#)

process.simpleAnalyzer = cms.EDAnalyzer(
	'SimpleJetAnalyzer',
    interestingCollections = cms.untracked.VInputTag([
        "selectedPatJets",
        "shiftedPatJetsEnDownForCorrMEt",
        "smearedPatJets",
        "smearedPatJetsResUp"
    ])
)


process.p = cms.Path(process.simpleAnalyzer)
