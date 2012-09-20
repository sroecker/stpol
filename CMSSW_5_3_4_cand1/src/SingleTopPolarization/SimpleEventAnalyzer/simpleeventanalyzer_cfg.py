import FWCore.ParameterSet.Config as cms

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/home/joosep/singletop/stpol/patTuple_slim_numEvent100.root'
#        'file:/hdfs/local/stpol/joosep/FEFF01BD-87DC-E111-BC9E-003048678F8E.root'
    )
)

process.demo = cms.EDAnalyzer('SimpleEventAnalyzer'
)


process.p = cms.Path(process.demo)
