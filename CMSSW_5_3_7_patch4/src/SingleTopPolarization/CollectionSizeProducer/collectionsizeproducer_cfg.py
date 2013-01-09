import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:myfile.root'
    )
)

# Producers
process.muonCollectionSizeProducer = cms.EDProducer('CollectionSizeProducer<reco::Muon>',
	vectorTag = cms.InputTag("muons")
)

process.photonCollectionSizeProducer = cms.EDProducer('CollectionSizeProducer<reco::Photon>',
	vectorTag = cms.InputTag("photons")
)

# Path
process.p = cms.Path(process.muonCollectionSizeProducer
                    *process.photonCollectionSizeProducer)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

process.e = cms.EndPath(process.out)

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
