import FWCore.ParameterSet.Config as cms

def PartonStudySetup(process, untaggedSrc="fwdMostLightJet"):
    process.cosThetaProducerTrueTop = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueTop"),
        jetSrc=cms.InputTag(untaggedSrc),
        leptonSrc=cms.InputTag("goodSignalLeptons")
    )

    process.cosThetaProducerTrueLepton = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTop"),
        jetSrc=cms.InputTag(untaggedSrc),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton")
    )

    process.cosThetaProducerTrueJet = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTop"),
        jetSrc=cms.InputTag("genParticleSelector", "trueLightJet"),
        leptonSrc=cms.InputTag("goodSignalLeptons")
    )

    #Select the generated top quark, light jet and charged lepton
    process.genParticleSelector = cms.EDProducer('GenParticleSelector',
         src=cms.InputTag("genParticles")
    )

    process.hasGenLepton = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("genParticleSelector", "trueLepton"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    process.cosThetaProducerTrueAll = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelector", "trueTop"),
        jetSrc=cms.InputTag("genParticleSelector", "trueLightJet"),
        leptonSrc=cms.InputTag("genParticleSelector", "trueLepton")
    )

    process.matrixCreator = cms.EDAnalyzer('TransferMatrixCreator',
        src = cms.InputTag("cosTheta", "cosThetaLightJet"),
        trueSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet")
    )

    process.leptonComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("goodSignalLeptons"),
        trueSrc = cms.InputTag("genParticleSelector", "trueLepton"),
        maxMass=cms.untracked.double(.3)
    )

    process.jetComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("untaggedJets"),
        trueSrc = cms.InputTag("genParticleSelector", "trueLightJet"),
        maxMass=cms.untracked.double(40.)
    )

    process.topComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("recoTop"),
        trueSrc = cms.InputTag("genParticleSelector", "trueTop"),
        maxMass=cms.untracked.double(300.)
    )

    process.partonStudyTrueSequence = cms.Sequence(
        process.genParticleSelector *
        process.hasGenLepton *
        process.cosThetaProducerTrueAll
    )

    process.partonStudyCompareSequence = cms.Sequence(
        process.hasGenLepton *
        process.cosThetaProducerTrueTop *
        process.cosThetaProducerTrueLepton *
        process.cosThetaProducerTrueJet *
        process.matrixCreator *
        process.leptonComparer *
        process.jetComparer *
        process.topComparer
    )
