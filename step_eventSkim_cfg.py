import FWCore.ParameterSet.Config as cms

def skimFilters(process):
    muonMinPt = 20
    muonEtaRange = [-4.5, 4.5]
    muonSource = "muons"
    process.looseMuonsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(muonSource),
    ptMin   = cms.double(muonMinPt),
    etaMin = cms.double(min(muonEtaRange)),
    etaMax = cms.double(max(muonEtaRange))
    )

    jetMinPt = 40
    jetEtaRange = [-4.5, 4.5]
    jetSource = "ak5PFJets"
    process.looseJetsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(jetSource),
    ptMin   = cms.double(jetMinPt),
    etaMin = cms.double(min(jetEtaRange)),
    etaMax = cms.double(max(jetEtaRange))
    )

    electronMinPt = 20
    electronEtaRange = [-4.5, 4.5]
    electronSource = "gsfElectrons"
    process.looseElectronsSkim = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag(electronSource),
    ptMin   = cms.double(electronMinPt),
    etaMin = cms.double(min(electronEtaRange)),
    etaMax = cms.double(max(electronEtaRange))
    )

    process.muonFilterSkim = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseMuonsSkim"),
      minNumber = cms.uint32(1),
    )

    process.jetFilterSkim = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseJetsSkim"),
      minNumber = cms.uint32(2),
    )

    process.electronFilterSkim = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseElectronsSkim"),
      minNumber = cms.uint32(1),
    )

    process.processedSkimEvents = cms.EDProducer("EventCountProducer")
    process.passMuonSkim = cms.EDProducer("EventCountProducer")
    process.passElectronSkim = cms.EDProducer("EventCountProducer")
    process.passJetSkim = cms.EDProducer("EventCountProducer")

    process.muonSkim = cms.Sequence(
        process.processedSkimEvents
        * process.looseMuonsSkim
        * process.muonFilterSkim
        * process.passMuonSkim
        * process.looseJetsSkim
        * process.jetFilterSkim
        * process.passJetSkim
    )
    process.electronSkim = cms.Sequence(
        process.processedSkimEvents
        * process.looseElectronsSkim
        * process.electronFilterSkim
        * process.passElectronSkim
        * process.looseJetsSkim
        * process.jetFilterSkim
        * process.passJetSkim
    )
