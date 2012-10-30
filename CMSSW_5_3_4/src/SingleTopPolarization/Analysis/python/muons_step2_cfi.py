import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

def MuonSetup(process, isMC, muonSrc="muonsWithIso"):

    muonSrc = "muonsWithIso"

    goodMuonCut = 'isPFMuon'                                                                       # general reconstruction property
    goodMuonCut += ' && isGlobalMuon'                                                                   # general reconstruction property
    goodMuonCut += ' && pt > 26.'                                                                       # transverse momentum
    goodMuonCut += ' && abs(eta) < 2.1'                                                                 # pseudo-rapisity range
    goodMuonCut += ' && normChi2 < 10.'                                                                  # muon ID: 'isGlobalMuonPromptTight'
    goodMuonCut += ' && userFloat("track_hitPattern_trackerLayersWithMeasurement") > 5'                              # muon ID: 'isGlobalMuonPromptTight'
    goodMuonCut += ' && userFloat("globalTrack_hitPattern_numberOfValidMuonHits") > 0'                               # muon ID: 'isGlobalMuonPromptTight'
    goodMuonCut += ' && abs(dB) < 0.2'                                                                  # 2-dim impact parameter with respect to beam spot (s. "PAT muon configuration" above)
    goodMuonCut += ' && userFloat("innerTrack_hitPattern_numberOfValidPixelHits") > 0'                               # tracker reconstruction
    goodMuonCut += ' && numberOfMatchedStations > 1'                                                    # muon chamber reconstruction
    goodMuonCut += ' && abs(userFloat("dz")) < 0.5'

    looseVetoMuonCut = "isPFMuon"
    looseVetoMuonCut += "&& (isGlobalMuon | isTrackerMuon)"
    looseVetoMuonCut += "&& pt > 10"
    looseVetoMuonCut += "&& abs(eta)<2.5"
    looseVetoMuonCut += ' && userFloat("rhoCorrRelIso") < 0.2'  # Delta beta corrections (factor 0.5)

    #isolated region
    goodSignalMuonCut = goodMuonCut
    goodSignalMuonCut += ' && userFloat("rhoCorrRelIso") < 0.12'

    #anti-isolated region
    goodQCDMuonCut = goodMuonCut
    goodQCDMuonCut += '&& userFloat("rhoCorrRelIso") < 0.5'
    goodQCDMuonCut += '&& userFloat("rhoCorrRelIso") > 0.3'

    process.goodSignalMuons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag(muonSrc), cut=cms.string(goodSignalMuonCut)
    )

    process.goodQCDMuons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag(muonSrc), cut=cms.string(goodQCDMuonCut)
    )

    process.looseVetoMuons = cms.EDFilter("CandViewSelector",
      src=cms.InputTag(muonSrc), cut=cms.string(looseVetoMuonCut)
    )

    process.oneIsoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("goodSignalMuons"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    #in mu path we must have 1 loose muon (== THE isolated muon)
    process.looseMuVetoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoMuons"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    #In Muon path we must have 0 loose electrons
    process.looseEleVetoMu = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("looseVetoElectrons"),
        minNumber=cms.uint32(0),
        maxNumber=cms.uint32(0),
    )

    process.muAndMETMT = cms.EDProducer('CandTransverseMassProducer',
        collections=cms.untracked.vstring(["patMETs", "goodSignalMuons"])
    )

    process.hasMuMETMT = cms.EDFilter('EventDoubleFilter',
        src=cms.InputTag("muAndMETMT"),
        min=cms.double(40),
        max=cms.double(9999)
    )

    process.recoNuProducerMu = cms.EDProducer('ReconstructedNeutrinoProducer',
        leptonSrc=cms.InputTag("goodSignalMuons"),
        bjetSrc=cms.InputTag("btaggedJets"),
        metSrc=cms.InputTag("patMETs"),
    )

def MuonPath(process, isMC):
    process.muPathPreCount = cms.EDProducer("EventCountProducer")

    process.efficiencyAnalyzerMu = cms.EDAnalyzer('EfficiencyAnalyzer'
    , histogrammableCounters = cms.untracked.vstring(["muPath"])
    , muPath = cms.untracked.vstring([
        "singleTopPathStep1MuPreCount",
        "singleTopPathStep1MuPostCount",
        "muPathPreCount",
        "muPathStepHLTsyncMuPostCount",
        "muPathOneIsoMuPostCount",
        "muPathLooseMuVetoMuPostCount",
        "muPathLooseEleVetoMuPostCount",
        "muPathNJetsPostCount",
        "muPathHasMuMETMTPostCount",
        "muPathMBTagsPostCount"
        ]
    ))

    process.muPath = cms.Path(
        process.muonsWithIso *
        process.elesWithIso *

        process.muPathPreCount *

        #Optionally select the HLT
        process.stepHLTsyncMu *

        #Select one isolated muon and veto additional loose muon/electron
        process.goodSignalMuons *
        process.goodQCDMuons *
        process.looseVetoMuons *
        process.oneIsoMu *
        process.looseMuVetoMu *
        process.looseVetoElectrons *
        process.looseEleVetoMu *

        #Do PU-jet cleaning, and select 2 good jets
        process.noPUJets *
        process.goodJets *
        process.nJets *

        #Select mu and MET invariant transverse mass
        process.muAndMETMT *
        process.hasMuMETMT *

        #Reconstruct the neutrino
        process.recoNuProducerMu *

        #Select b-tagged jets and events with ==1 btag
        process.btaggedJets *
        process.untaggedJets *
        process.mBTags *

        #Reconstruct the top quark and calculate the cosTheta* variable
        process.recoTopMu *
        process.cosThetaProducerMu *
        process.efficiencyAnalyzerMu
    )
    if isMC:
        #in MC we need to smear the reconstucted jet pt, E
        process.muPath.insert(process.muPath.index(process.noPUJets)+1, process.smearedJets)

        #process.muPath.insert(0, process.partonStudyTrueSequence)
        process.muPath.insert(
            process.muPath.index(process.cosThetaProducerMu)+1,
            process.partonStudyCompareSequence
        )

    #Count number of events passing the selection filters
    eventCounting.countAfter(process, process.muPath,
        [
        "stepHLTsyncMu",
        "oneIsoMu",
        "looseMuVetoMu",
        "looseEleVetoMu",
        "hasMuMETMT",
        "nJets",
        "mBTags"
        ]
    )

