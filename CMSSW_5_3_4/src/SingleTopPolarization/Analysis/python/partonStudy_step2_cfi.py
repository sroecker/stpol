import FWCore.ParameterSet.Config as cms

def PartonStudySetup(process):
    process.cosThetaProducerTrueTopMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelectorMu", "trueTop"),
        jetSrc=cms.InputTag("untaggedJets"),
        leptonSrc=cms.InputTag("goodSignalMuons")
    )

    process.cosThetaProducerTrueLeptonMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTopMu"),
        jetSrc=cms.InputTag("untaggedJets"),
        leptonSrc=cms.InputTag("genParticleSelectorMu", "trueLepton")
    )

    process.cosThetaProducerTrueJetMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTopMu"),
        jetSrc=cms.InputTag("genParticleSelectorMu", "trueLightJet"),
        leptonSrc=cms.InputTag("goodSignalMuons")
    )

    #Select the generated top quark, light jet and charged lepton
    process.genParticleSelectorMu = cms.EDProducer('GenParticleSelector',
         src=cms.InputTag("genParticles")
    )

    process.hasMuon = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("genParticleSelectorMu", "trueLepton"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    process.trueCosThetaProducerMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelectorMu", "trueTop"),
        jetSrc=cms.InputTag("genParticleSelectorMu", "trueLightJet"),
        leptonSrc=cms.InputTag("genParticleSelectorMu", "trueLepton")
    )

    process.matrixCreator = cms.EDAnalyzer('TransferMatrixCreator',
        src = cms.InputTag("cosThetaProducerMu", "cosThetaLightJet"),
        trueSrc = cms.InputTag("trueCosThetaProducerMu", "cosThetaLightJet")
    )

    process.leptonComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("goodSignalLeptons"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueLepton"),
        maxMass=cms.untracked.double(.3)
    )

    process.jetComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("untaggedJets"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueLightJet"),
        maxMass=cms.untracked.double(40.)
    )

    process.topComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("recoTopMu"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueTop"),
        maxMass=cms.untracked.double(300.)
    )

    process.partonStudyTrueSequence = cms.Sequence(process.genParticleSelectorMu * process.hasMuon * process.trueCosThetaProducerMu)
    process.partonStudyCompareSequence = cms.Sequence(
        process.cosThetaProducerTrueTopMu *
        process.cosThetaProducerTrueLeptonMu *
        process.cosThetaProducerTrueJetMu *
        process.matrixCreator *
        process.leptonComparer *
        process.jetComparer *
        process.topComparer
        )
