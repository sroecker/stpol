import FWCore.ParameterSet.Config as cms

def JetSetup(process, isMC, doDebug, bTagType="combinedSecondaryVertexMVABJetTags", bTagCut=0.679, nJets=2, nBTags=1, cutJets=True):
    if cutJets:
        print "CUT\tJets: Using %d jets, %d tags" % (nJets, nBTags)
    else:
        print "CUT\tJets: keeping all events with >=1 jet and >=0 btag"
        
    if isMC:
        jetCut = 'userFloat("pt_smear") > 40.'
    else:
        jetCut = 'pt > 40'

    jetCut += ' && abs(eta) < 4.7'                                        # pseudo-rapidity range
    jetCut += ' && numberOfDaughters > 1'                                 # PF jet ID:
    jetCut += ' && neutralHadronEnergyFraction < 0.99'                    # PF jet ID:
    jetCut += ' && neutralEmEnergyFraction < 0.99'                        # PF jet ID:
    jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'  # PF jet ID:
    jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)'   # PF jet ID:
    jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'          # PF jet ID:


    process.noPUJets = cms.EDProducer('CleanNoPUJetProducer',
        jetSrc = cms.InputTag("selectedPatJets"),
        PUidMVA = cms.InputTag("puJetMva", "fullDiscriminant", "PAT"),
        PUidFlag = cms.InputTag("puJetMva", "fullId", "PAT"),
        PUidVars = cms.InputTag("puJetId", "", "PAT"),
    )

    if isMC:
        process.smearedJets = cms.EDProducer('JetMCSmearProducer',
            src=cms.InputTag("noPUJets"),
            reportMissingGenJet=cms.untracked.bool(doDebug)
        )

    process.goodJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("smearedJets" if isMC else 'noPUJets'),
        cut=cms.string(jetCut)
    )

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (bTagType, bTagCut)

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
        bDiscriminator = cms.string(bTagType),
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
        minNumber=cms.uint32(nJets if cutJets else 1),
        maxNumber=cms.uint32(nJets if cutJets else 4),
    )

    #Require exactly M bTags, otherwise 0...3 bJets
    process.mBTags = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("btaggedJets"),
        minNumber=cms.uint32(nBTags if cutJets else 0),
        maxNumber=cms.uint32(nBTags if cutJets else 3),
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

    if isMC:
        process.jetSequence.insert(process.jetSequence.index(process.noPUJets)+1, process.smearedJets)
