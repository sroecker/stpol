import FWCore.ParameterSet.Config as cms

def JetSetup(process, isMC, doDebug, bTag="combinedSecondaryVertexBJetTags", bTagCut=0.679):
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

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (bTag, bTagCut)

    process.btaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr)
    )

    process.untaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr.replace(">=", "<"))
    )

    #Require exactly N jets
    process.nJets = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodJets"),
        minNumber=cms.uint32(2),
        maxNumber=cms.uint32(2),
    )

    #Require exactly M bTags of the given type
    process.mBTags = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("btaggedJets"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )
