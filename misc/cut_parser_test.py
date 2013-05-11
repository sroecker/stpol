import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations   = cms.untracked.vstring(
                                              'cout',
                    ),
       debugModules   = cms.untracked.vstring('myProducerLabel'),
       cout       = cms.untracked.PSet(
                       threshold = cms.untracked.string('DEBUG')
        ),
)


process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1_04_19/c9249c44a215ffeb8c9ba40f59092334/output_100_1_QDL.root'
    )
)

process.muons1 = cms.EDFilter("CandViewSelector",
  src=cms.InputTag("muonsWithID"), cut=cms.string("pt>50&&eta<2.4")
)
process.muons2 = cms.EDFilter("CandViewSelector",
  src=cms.InputTag("muonsWithID"), cut=cms.string("pt>50 && eta<2.4")
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(process.muons1*process.muons2)

process.e = cms.EndPath(process.out)
