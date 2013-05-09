import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.calibrations_cfg as Calibrations

import logging
logger = logging.getLogger("JetSetup")

def JetSetup(process, conf):

    jetCut = 'pt > %f' % conf.Jets.ptCut
    jetCut += ' && abs(eta) < %f' % conf.Jets.etaCut
    jetCut += ' && numberOfDaughters > 1'
    #jetCut += ' && neutralHadronEnergyFraction < 0.99'
    #Use the new hadron energy fraction definition
    #https://hypernews.cern.ch/HyperNews/CMS/get/JetMET/1429.html
    jetCut += ' && (neutralHadronEnergy() + HFHadronEnergy())/energy() < 0.99'
    jetCut += ' && neutralEmEnergyFraction < 0.99'
    jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'
    jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)'
    jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'

    process.skimJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag(conf.Jets.source),
        cut=cms.string('pt>15')
    )

    if(conf.Jets.source == "selectedPatJets"):
        process.noPUJets = cms.EDProducer('CleanNoPUJetProducer',
            jetSrc = cms.InputTag("skimJets"),
            PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
            PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
            PUidVars = cms.InputTag("puJetId", "", "PAT"),
            isOriginal=cms.bool(True)
        )
    else:
        process.noPUJets = cms.EDProducer('CleanNoPUJetProducer',
            jetSrc = cms.InputTag("skimJets"),
            PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
            PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
            PUidVars = cms.InputTag("puJetId", "", "PAT"),
            isOriginal=cms.bool(False)
        )

#    if conf.isMC:
#        process.smearedJets = cms.EDProducer('JetMCSmearProducer',
#            src=cms.InputTag("noPUJets"),
#            reportMissingGenJet=cms.untracked.bool(conf.doDebug)
#        )

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (conf.Jets.bTagDiscriminant, conf.Jets.BTagWorkingPointVal())


    process.deltaRJets = cms.EDProducer("DeltaRProducer",
        leptonSrc=cms.InputTag("goodSignalLeptons"),
        jetSrc=cms.InputTag("noPUJets")
        #jetSrc=cms.InputTag(conf.Jets.source)
    )

    process.goodJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("deltaRJets"),
        cut=cms.string(jetCut)
    )

    process.goodJetsRMSCleaned = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr + " || (!(%s) && userFloat('rms')<0.025)" % bTagCutStr)
    )

    #B-tagging efficiencies
    if conf.isMC:
        #B-jet b-tagging efficiency
        process.trueBJets = cms.EDFilter("CandViewSelector",
            src=cms.InputTag("goodJets"),
            cut=cms.string("abs(partonFlavour()) == 5")
        )
        process.btaggedTrueBJets = cms.EDFilter(
            "CandViewSelector",
            src=cms.InputTag("trueBJets"),
            cut=cms.string(bTagCutStr)
        )
        process.trueBJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("trueBJets")
        )
        process.btaggedTrueBJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("btaggedTrueBJets")
        )
        process.bJetBTagEffSequence = cms.Sequence(
            process.trueBJets *
            process.btaggedTrueBJets *
            process.trueBJetCount *
            process.btaggedTrueBJetCount
        )

        #C-jet b-tagging efficiency
        process.trueCJets = cms.EDFilter("CandViewSelector",
            src=cms.InputTag("goodJets"),
            cut=cms.string("abs(partonFlavour()) == 4")
        )
        process.btaggedTrueCJets = cms.EDFilter(
            "CandViewSelector",
            src=cms.InputTag("trueCJets"),
            cut=cms.string(bTagCutStr)
        )
        process.trueCJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("trueCJets")
        )
        process.btaggedTrueCJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("btaggedTrueCJets")
        )
        process.cJetBTagEffSequence = cms.Sequence(
            process.trueCJets *
            process.btaggedTrueCJets *
            process.trueCJetCount *
            process.btaggedTrueCJetCount
        )

        #light-jet b-tagging efficiency
        process.trueLJets = cms.EDFilter("CandViewSelector",
            src=cms.InputTag("goodJets"),
            #cut=cms.string("abs(partonFlavour()) <= 3 || abs(partonFlavour()) == 9 || abs(partonFlavour()) == 21") #uds, gluons
            cut=cms.string("abs(partonFlavour()) != 4 && abs(partonFlavour()) != 5") #anything not a b or a c
        )
        process.btaggedTrueLJets = cms.EDFilter(
            "CandViewSelector",
            src=cms.InputTag("trueLJets"),
            cut=cms.string(bTagCutStr)
        )
        process.trueLJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("trueLJets")
        )
        process.btaggedTrueLJetCount = cms.EDProducer(
            "CollectionSizeProducer<reco::Candidate>",
            src = cms.InputTag("btaggedTrueLJets")
        )
        process.lJetBTagEffSequence = cms.Sequence(
            process.trueLJets *
            process.btaggedTrueLJets *
            process.trueLJetCount *
            process.btaggedTrueLJetCount
        )


        process.trueLJets = cms.EDFilter("CandViewSelector",
            src=cms.InputTag("goodJets"),
            cut=cms.string("abs(partonFlavour()) <= 3")
        )

    process.goodJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodJetsRMSCleaned")
    )


    process.btaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJetsRMSCleaned"),
        cut=cms.string(bTagCutStr)
    )

    process.bJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedJets")
    )

    #invert the b-tag cut
    process.untaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJetsRMSCleaned"),
        cut=cms.string(bTagCutStr.replace(">=", "<"))
    )

    process.lightJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("untaggedJets")
    )

    #Select the most forward untagged jet by absolute eta
    process.fwdMostLightJet = cms.EDFilter(
        'LargestAbsEtaCandViewProducer',
        src = cms.InputTag("goodJetsRMSCleaned"),
        maxNumber = cms.uint32(1)
    )

    #Gets the b-tagged jet with the highest b discriminator value
    process.highestBTagJet = cms.EDFilter(
        'LargestBDiscriminatorJetViewProducer',
        src = cms.InputTag("goodJetsRMSCleaned"),
        maxNumber = cms.uint32(1),
        bDiscriminator = cms.string(conf.Jets.bTagDiscriminant),
        reverse = cms.bool(False)
    )

    #Take the jet with the lowest overall b-discriminator value as the light jet
    process.lowestBTagJet = process.highestBTagJet.clone(
        src = cms.InputTag("goodJetsRMSCleaned"),
        reverse = cms.bool(True)
    )

    #Events failing the following jet cuts are not processed further (deliberately loose)
    process.nJets = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodJetsRMSCleaned"),
        minNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 2),
        maxNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 9999),
    )
    process.mBTags = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("btaggedJets"),
        minNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 0),
        maxNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 9999),
    )

    #Require at least 1 untagged jet
    process.oneUntaggedJet = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("untaggedJets"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(9999999),
    )

    if conf.isMC:
        effs_2J = Calibrations.getEfficiencies(2, conf.subChannel)
        effs_3J = Calibrations.getEfficiencies(3, conf.subChannel)
        #if conf.subChannel in (Calibrations.bTaggingEfficiencies_2J.keys()+Calibrations.bTaggingEfficiencies_3J.keys()):
        #    sampleBEffs_2J = Calibrations.bTaggingEfficiencies_2J[conf.subChannel]
        #    sampleBEffs_3J = Calibrations.bTaggingEfficiencies_3J[conf.subChannel]
        #    logging.info("B-tagging efficiencies for subChannel %s loaded" % conf.subChannel)
        #else:
        #    logging.warning("B-tagging efficiencies for subChannel %s not defined" % conf.subChannel)
        #    raise Exception("B-tagging efficiencies not defined")
        #    sampleBEffs_2J = Calibrations.BTaggingEfficiency.default
        #    sampleBEffs_3J = Calibrations.BTaggingEfficiency.default
        #logger.debug("Using the following calibration coefficients for sample {0}: {1}".format(conf.subChannel, sampleBEffs))

        #The b-tag weight calculation is different for each required n-jet/m-btag bin
        process.bTagWeightProducerNJMT = cms.EDProducer('BTagSystematicsWeightProducer',
            src=cms.InputTag("goodJetsRMSCleaned"),
            nJets=cms.uint32(0),
            nTags=cms.uint32(0),
            nJetSrc=cms.InputTag("goodJetCount"),
            nTagSrc=cms.InputTag("bJetCount"),
            effBin2J=cms.double(effs_2J.eff_b),
            effCin2J=cms.double(effs_2J.eff_c),
            effLin2J=cms.double(effs_2J.eff_l),
            effBin3J=cms.double(effs_3J.eff_b),
            effCin3J=cms.double(effs_3J.eff_c),
            effLin3J=cms.double(effs_3J.eff_l),
            algo=cms.string(conf.Jets.bTagWorkingPoint)
        )
        #process.bTagWeightProducer3J1T = process.bTagWeightProducerNJMT.clone(nJets=cms.uint32(3), nTags=cms.uint32(1))
        #process.bTagWeightProducer3J2T = process.bTagWeightProducerNJMT.clone(nJets=cms.uint32(3), nTags=cms.uint32(2))
        #process.bTagWeightProducer3J0T = process.bTagWeightProducerNJMT.clone(nJets=cms.uint32(3), nTags=cms.uint32(0))
        #process.bTagWeightProducer2J0T = process.bTagWeightProducerNJMT.clone(nJets=cms.uint32(2), nTags=cms.uint32(0))

        process.bEffSequence = cms.Sequence(
            process.bJetBTagEffSequence *
            process.cJetBTagEffSequence *
            process.lJetBTagEffSequence *
            process.bTagWeightProducerNJMT
            #process.bTagWeightProducer3J1T *
            #process.bTagWeightProducer3J2T *
            #process.bTagWeightProducer3J0T *
            #process.bTagWeightProducer2J0T
        )


    process.jetSequence = cms.Sequence()

    process.jetSequence +=(
      process.skimJets *
      process.noPUJets *
      process.deltaRJets *
      process.goodJets *
      process.goodJetsRMSCleaned *

      process.goodJetCount *

      process.btaggedJets *
      process.bJetCount *
      process.untaggedJets *
      process.lightJetCount
    )

    if conf.isMC:
        process.jetSequence += process.bEffSequence

    process.jetSequence += cms.Sequence(
        process.fwdMostLightJet *
        process.highestBTagJet *
        process.lowestBTagJet
    )

    print "goodJets cut = %s" % process.goodJetsRMSCleaned.cut
    print "btaggedJets cut = %s" % process.btaggedJets.cut

    #if conf.isMC:
    #    process.jetSequence.insert(process.jetSequence.index(process.noPUJets)+1, process.smearedJets)
    if conf.doDebug:
        #process.sourceJetAnalyzer = cms.EDAnalyzer("SimpleJetAnalyzer", interestingCollections=cms.untracked.VInputTag(conf.Jets.source))
        #process.jetSequence.insert(0, process.sourceJetAnalyzer)
        process.jetAnalyzer = cms.EDAnalyzer("SimpleJetAnalyzer", interestingCollections=cms.untracked.VInputTag(conf.Jets.source, "goodJetsRMSCleaned"))
        process.jetSequence += process.jetAnalyzer

    print process.jetSequence
