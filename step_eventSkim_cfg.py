import FWCore.ParameterSet.Config as cms

def skimFilters(process):
    muonMinPt = 20
    muonEtaRange = [-4.5, 4.5]
    process.looseMuons = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag("muons"),
    ptMin   = cms.double(muonMinPt),
    etaMin = cms.double(min(muonEtaRange)),
    etaMax = cms.double(max(muonEtaRange))
    )

    jetMinPt = 40
    jetEtaRange = [-4.5, 4.5]
    process.looseJets = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag("ak5PFJets"),
    ptMin   = cms.double(jetMinPt),
    etaMin = cms.double(min(jetEtaRange)),
    etaMax = cms.double(max(jetEtaRange))
    )

    electronMinPt = 20
    electronEtaRange = [-4.5, 4.5]
    process.looseElectrons = cms.EDFilter("EtaPtMinCandViewSelector",
    src = cms.InputTag("gsfElectrons"),
    ptMin   = cms.double(electronMinPt),
    etaMin = cms.double(min(electronEtaRange)),
    etaMax = cms.double(max(electronEtaRange))
    )

    process.muonFilter = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseMuons"),
      minNumber = cms.uint32(1),
    )

    process.jetFilter = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseJets"),
      minNumber = cms.uint32(2),
    )

    process.electronFilter = cms.EDFilter("CandViewCountFilter",
      src = cms.InputTag("looseElectrons"),
      minNumber = cms.uint32(1),
    )

    process.processedSkimEvents = cms.EDProducer("EventCountProducer")
    process.passMuonSkim = cms.EDProducer("EventCountProducer")
    process.passJetSkim = cms.EDProducer("EventCountProducer")
    process.skim_muon = cms.Sequence(process.processedSkimEvents*process.looseMuons*process.muonFilter*process.passMuonSkim*process.looseJets*process.jetFilter*process.passJetSkim)
