import FWCore.ParameterSet.Config as cms

def JetSetup(process, conf):

#    if cutJets:
#        print "CUT\tJets: Using %d jets, %d tags" % (nJets, nBTags)
#    else:
#        print "CUT\tJets: keeping all events with >=1 jet and >=0 btag"
#
    if conf.isMC:
        jetCut = 'userFloat("pt_smear") > %f' % conf.Jets.ptCut
    else:
        jetCut = 'pt > %f' % conf.Jets.ptCut

    jetCut += ' && abs(eta) < %f' % conf.Jets.etaCut
    jetCut += ' && numberOfDaughters > 1'
    jetCut += ' && neutralHadronEnergyFraction < 0.99'
    jetCut += ' && neutralEmEnergyFraction < 0.99'
    jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'
    jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)'
    jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'


    process.noPUJets = cms.EDProducer('CleanNoPUJetProducer',
        jetSrc = cms.InputTag("selectedPatJets"),
        PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
        PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
        PUidVars = cms.InputTag("puJetId", "", "PAT"),
    )

    if conf.isMC:
        process.smearedJets = cms.EDProducer('JetMCSmearProducer',
            src=cms.InputTag("noPUJets"),
            reportMissingGenJet=cms.untracked.bool(conf.doDebug)
        )

    process.goodJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("smearedJets" if conf.isMC else 'noPUJets'),
        cut=cms.string(jetCut)
    )

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (conf.Jets.bTagDiscriminant, conf.Jets.BTagWorkingPointVal())

    process.btaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr)
    )

    process.bJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("btaggedJets")
    )

    #invert the b-tag cut
    process.untaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr.replace(">=", "<"))
    )

    process.lightJetCount = cms.EDProducer(
        "CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("untaggedJets")
    )

    #Select the most forward untagged jet by absolute eta
    process.fwdMostLightJet = cms.EDFilter(
        'LargestAbsEtaCandViewProducer',
        src = cms.InputTag("untaggedJets"),
        maxNumber = cms.uint32(1)
    )

    process.highestBTagJet = cms.EDFilter(
        'LargestBDiscriminatorJetViewProducer',
        src = cms.InputTag("btaggedJets"),
        maxNumber = cms.uint32(1),
        bDiscriminator = cms.string(conf.Jets.bTagDiscriminant),
        reverse = cms.bool(False)
    )

    #Take the jet with the lowest overall b-discriminator value as the light jet
    process.lowestBTagJet = process.highestBTagJet.clone(
        src = cms.InputTag("untaggedJets"),
        reverse = cms.bool(True)
    )

    #Require exactly N jets if cutting on jets, otherwise 1...4 jets
    process.nJets = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodJets"),
        minNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 1),
        maxNumber=cms.uint32(conf.Jets.nJets if conf.Jets.cutJets else 4),
    )

    #Require exactly M bTags, otherwise 1...3 bJets
    process.mBTags = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("btaggedJets"),
        minNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 1),
        maxNumber=cms.uint32(conf.Jets.nBTags if conf.Jets.cutJets else 3),
    )

    process.jetSequence = cms.Sequence(
      process.noPUJets *
      process.goodJets *
      process.btaggedJets *
      process.untaggedJets *
      process.bJetCount *
      process.lightJetCount *
      process.fwdMostLightJet *
      process.highestBTagJet *
      process.lowestBTagJet
    )
    print "goodJets cut = %s" % process.goodJets.cut
    print "btaggedJets cut = %s" % process.btaggedJets.cut

    if conf.isMC:
        process.jetSequence.insert(process.jetSequence.index(process.noPUJets)+1, process.smearedJets)
