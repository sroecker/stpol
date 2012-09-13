import FWCore.ParameterSet.Config as cms

muonMinPt = 10
muonEtaRange = [-4.5, 4.5]
looseMuons = cms.EDProducer("EtaPtMinCandViewSelector",
src = cms.InputTag("muons"),
ptMin   = cms.double(muonMinPt),
etaMin = cms.double(min(muonEtaRange)),
etaMax = cms.double(max(muonEtaRange))
)

jetMinPt = 20
jetEtaRange = [-4.5, 4.5]
looseJets = cms.EDProducer("EtaPtMinCandViewSelector",
src = cms.InputTag("ak5PFJets"),
ptMin   = cms.double(jetMinPt),
etaMin = cms.double(min(jetEtaRange)),
etaMax = cms.double(max(jetEtaRange))
)

electronMinPt = 10
electronEtaRange = [-4.5, 4.5]
looseElectrons = cms.EDProducer("EtaPtMinCandViewSelector",
src = cms.InputTag("gsfElectrons"),
ptMin   = cms.double(electronMinPt),
etaMin = cms.double(min(electronEtaRange)),
etaMax = cms.double(max(electronEtaRange))
)

muonFilter = cms.EDFilter("CandViewCountFilter",
  src = cms.InputTag("looseMuons"),
  minNumber = cms.uint32(1),
)

jetFilter = cms.EDFilter("CandViewCountFilter",
  src = cms.InputTag("looseJets"),
  minNumber = cms.uint32(2),
)

electronFilter = cms.EDFilter("CandViewCountFilter",
  src = cms.InputTag("looseElectrons"),
  minNumber = cms.uint32(1),
)

skim_muon = cms.Sequence(looseMuons*looseJets*muonFilter)
skim_electron = cms.Sequence(looseElectrons*looseJets*electronFilter)
