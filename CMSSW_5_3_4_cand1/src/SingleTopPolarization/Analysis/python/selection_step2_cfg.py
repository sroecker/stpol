import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.eventCounting import *

process = cms.Process("STPOLSEL2")
countProcessed(process)

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(""
    )
)

#-------------------------------------------------
# Jets
#-------------------------------------------------

jetCut = 'pt > 20.'                                                   # transverse momentum
jetCut += ' && abs(eta) < 5.0'                                        # pseudo-rapidity range
jetCut += ' && numberOfDaughters > 1'                                 # PF jet ID:
jetCut += ' && neutralHadronEnergyFraction < 0.99'                    # PF jet ID:
jetCut += ' && neutralEmEnergyFraction < 0.99'                        # PF jet ID:
jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'   # PF jet ID:
jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)' # PF jet ID:
jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'          # PF jet ID:

process.goodJets = cms.EDFilter("CandViewSelector",
    src = cms.InputTag('selectedPatJets'),
    cut = cms.string(jetCut)
)

process.bTagsTCHPtight = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag("goodJets"),
    cut = cms.string('bDiscriminator("trackCountingHighPurBJetTags") > 3.41')
)

process.bTagsCSVmedium = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag("goodJets"),
    cut = cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.679')
)

process.bTagsCSVtight = cms.EDFilter(
    "CandViewSelector",
    src = cms.InputTag("bTagsCSVmedium"),
    cut = cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.898')
)

#Require exactly N jets
process.nJets = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodJets"),
    minNumber = cms.uint32(2),
    maxNumber = cms.uint32(2),
)

#Require exactly M bTags of the given type
process.mBTags = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("bTagsTCHPtight"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)


#-------------------------------------------------
# Muons
#-------------------------------------------------

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
looseVetoMuonCut += ' && userFloat("deltaBetaCorrRelIso") < 0.2' # Delta beta corrections (factor 0.5)

#isolated region
goodSignalMuonCut = goodMuonCut
goodSignalMuonCut += ' && userFloat("deltaBetaCorrRelIso") < 0.12'

#anti-isolated region
goodQCDMuonCut = goodMuonCut
goodQCDMuonCut += '&& userFloat("deltaBetaCorrRelIso") < 0.5'
goodQCDMuonCut += '&& userFloat("deltaBetaCorrRelIso") > 0.3'

process.goodSignalMuons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("muonsWithID"), cut = cms.string(goodSignalMuonCut)
)

process.goodQCDMuons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("muonsWithID"), cut = cms.string(goodQCDMuonCut)
)

process.looseVetoMuons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("muonsWithID"), cut = cms.string(looseVetoMuonCut)
)

process.oneIsoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodSignalMuons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#in mu path we must have 1 loose muon (== THE isolated muon)
process.looseMuVetoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoMuons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#In Muon path we must have 0 loose electrons
process.looseEleVetoMu = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoElectrons"),
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(0),
)

#-------------------------------------------------
# Electrons
#-------------------------------------------------

goodElectronCut = "pt>30"
goodElectronCut += "&& abs(eta)<2.5"
goodElectronCut += "&& !(1.4442 < abs(superCluster.eta) < 1.5660)"
goodElectronCut += "&& passConversionVeto()"
goodElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"

goodSignalElectronCut = goodElectronCut
goodSignalElectronCut += '&& userFloat("rhoCorrRelIso") < 0.1'

goodQCDElectronCut = goodElectronCut
goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") > 0.2'
goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") < 0.5'

looseVetoElectronCut = "pt > 20"
looseVetoElectronCut += "&& abs(eta) < 2.5"
looseVetoElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
looseVetoElectronCut += '&& userFloat("rhoCorrRelIso") < 0.15'

process.goodSignalElectrons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("elesWithIso"), cut = cms.string(goodSignalElectronCut)
)

process.goodQCDElectrons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("elesWithIso"), cut = cms.string(goodQCDElectronCut)
)

process.looseVetoElectrons = cms.EDFilter("CandViewSelector",
  src = cms.InputTag("elesWithIso"), cut = cms.string(looseVetoElectronCut)
)

process.oneIsoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("goodSignalElectrons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#In Electron path we must have 1 loose electron (== the isolated electron)
process.looseEleVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoElectrons"),
    minNumber = cms.uint32(1),
    maxNumber = cms.uint32(1),
)

#In Electron path we must have 0 loose muons
process.looseMuVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src = cms.InputTag("looseVetoMuons"),
    minNumber = cms.uint32(0),
    maxNumber = cms.uint32(0),
)

#-----------------------------------------------
# Paths
#-----------------------------------------------

process.muPathPreCount = cms.EDProducer("EventCountProducer")
process.muPath = cms.Path(
    process.muPathPreCount *
    process.goodSignalMuons * 
    process.goodQCDMuons * 
    process.looseVetoMuons *
    process.oneIsoMu *
    process.looseMuVetoMu *
    process.looseVetoElectrons *
    process.looseEleVetoMu *
    process.goodJets *
    process.nJets *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.mBTags
)
countAfter(process, process.muPath, ["oneIsoMu", "looseMuVetoMu", "looseEleVetoMu", "nJets", "mBTags"])

process.elePathPreCount = cms.EDProducer("EventCountProducer")
process.elePath = cms.Path(
    process.elePathPreCount *
    process.goodSignalElectrons * 
    process.goodQCDElectrons * 
    process.looseVetoElectrons *
    process.oneIsoEle * 
    process.looseEleVetoEle *
    process.looseVetoMuons *
    process.looseMuVetoEle *
    process.goodJets *
    process.nJets *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.mBTags
)
countAfter(process, process.elePath, ["oneIsoEle", "looseEleVetoEle", "looseMuVetoEle", "nJets", "mBTags"])


#-----------------------------------------------
# Outpath
#-----------------------------------------------

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('out_step2.root'),
     SelectEvents = cms.untracked.PSet(
         SelectEvents = cms.vstring(['muPath', 'elePath'])
     ),
    outputCommands = cms.untracked.vstring(
        'keep *',
        'drop patElectrons_looseVetoElectrons__PAT',
        'drop patMuons_looseVetoMuons__PAT',
    )
)
process.outpath = cms.EndPath(process.out)


#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)
