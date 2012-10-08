import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.eventCounting import *

process = cms.Process("STPOLSEL2")
countProcessed(process)

doDebug = True

if doDebug:
    process.load("FWCore.MessageLogger.MessageLogger_cfi")
    process.MessageLogger = cms.Service("MessageLogger",
           destinations=cms.untracked.vstring(
                                                  'cout',
                                                  'debug'
                        ),
           debugModules=cms.untracked.vstring('*'),
           cout=cms.untracked.PSet(
            threshold=cms.untracked.string('INFO')
            ),
           debug=cms.untracked.PSet(
            threshold=cms.untracked.string('DEBUG')
            ),
    )
else:
    process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet(input=cms.untracked.int32(-1))

process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames=cms.untracked.vstring(""
    )
)

#-------------------------------------------------
# Jets
#-------------------------------------------------

jetCut = 'userFloat("pt_smear") > 40.'                                                   # transverse momentum
jetCut += ' && abs(eta) < 5.0'                                        # pseudo-rapidity range
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

process.smearedJets = cms.EDProducer('JetMCSmearProducer',
    src=cms.InputTag("noPUJets")
)

process.goodJets = cms.EDFilter("CandViewSelector",
    src=cms.InputTag('smearedJets'),
    cut=cms.string(jetCut)
)

process.bTagsTCHPtight = cms.EDFilter(
    "CandViewSelector",
    src=cms.InputTag("goodJets"),
    cut=cms.string('bDiscriminator("trackCountingHighPurBJetTags") >= 3.41')
)

process.untaggedTCHPtight = cms.EDFilter(
    "CandViewSelector",
    src=cms.InputTag("goodJets"),
    cut=cms.string('bDiscriminator("trackCountingHighPurBJetTags") < 3.41')
)

process.bTagsCSVmedium = cms.EDFilter(
    "CandViewSelector",
    src=cms.InputTag("goodJets"),
    cut=cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.679')
)

process.bTagsCSVtight = cms.EDFilter(
    "CandViewSelector",
    src=cms.InputTag("bTagsCSVmedium"),
    cut=cms.string('bDiscriminator("combinedSecondaryVertexBJetTags") > 0.898')
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
    src=cms.InputTag("bTagsTCHPtight"),
    minNumber=cms.uint32(1),
    maxNumber=cms.uint32(1),
)


#-------------------------------------------------
# Muons
#-------------------------------------------------
process.muonsWithIso = cms.EDProducer(
  'MuonIsolationProducer',
  leptonSrc = cms.InputTag("muonsWithID"),
  rhoSrc = cms.InputTag("kt6PFJets", "rho"),
  dR = cms.double(0.4)
)

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
    leptonSrc=cms.InputTag("goodSignalLeptons"),
    bjetSrc=cms.InputTag("bTagsTCHPtight"),
    metSrc=cms.InputTag("patMETs"),
)

# process.topsFromMu = cms.EDProducer('SimpleCompositeCandProducer',
#     sources=cms.VInputTag(["recoNu", "bTagsTCHPtight", "goodSignalMuons"])
# )

#-------------------------------------------------
# Electrons
#-------------------------------------------------

process.elesWithIso = cms.EDProducer(
  'ElectronIsolationProducer',
  leptonSrc = cms.InputTag("selectedPatElectrons"),
  rhoSrc = cms.InputTag("kt6PFJets", "rho"),
  dR = cms.double(0.4)
)

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
  src=cms.InputTag("elesWithIso"), cut=cms.string(goodSignalElectronCut)
)

process.goodQCDElectrons = cms.EDFilter("CandViewSelector",
  src=cms.InputTag("elesWithIso"), cut=cms.string(goodQCDElectronCut)
)

process.looseVetoElectrons = cms.EDFilter("CandViewSelector",
  src=cms.InputTag("elesWithIso"), cut=cms.string(looseVetoElectronCut)
)

process.oneIsoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src=cms.InputTag("goodSignalElectrons"),
    minNumber=cms.uint32(1),
    maxNumber=cms.uint32(1),
)

#In Electron path we must have 1 loose electron (== the isolated electron)
process.looseEleVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src=cms.InputTag("looseVetoElectrons"),
    minNumber=cms.uint32(1),
    maxNumber=cms.uint32(1),
)

#In Electron path we must have 0 loose muons
process.looseMuVetoEle = cms.EDFilter(
    "PATCandViewCountFilter",
    src=cms.InputTag("looseVetoMuons"),
    minNumber=cms.uint32(0),
    maxNumber=cms.uint32(0),
)

process.goodMETs = cms.EDFilter("CandViewSelector",
  src=cms.InputTag("patMETs"),
  cut=cms.string("pt>35")
)

process.hasMET = cms.EDFilter(
    "PATCandViewCountFilter",
    src=cms.InputTag("goodMETs"),
    minNumber=cms.uint32(1),
    maxNumber=cms.uint32(1),
)

process.recoNuProducerEle = cms.EDProducer('ReconstructedNeutrinoProducer',
    leptonSrc=cms.InputTag("goodSignalLeptons"),
    bjetSrc=cms.InputTag("bTagsTCHPtight"),
    metSrc=cms.InputTag("goodMETs"),
)

#-----------------------------------------------
# Treemaking
#-----------------------------------------------


def treeCollection(collection_, maxElems_, varlist):
    varVPSet = cms.untracked.VPSet()
    for v in varlist:
        pset = cms.untracked.PSet(tag=cms.untracked.string(v[0]), expr=cms.untracked.string(v[1]), )
        varVPSet.append(pset)
    ret = cms.untracked.PSet(
        collection=cms.untracked.string(collection_),
        maxElems=cms.untracked.int32(maxElems_),
        variables=varVPSet
    )
    return ret

process.treesMu = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
        collections = cms.untracked.VPSet(treeCollection("goodSignalMuons", 1,
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["deltaBetaCorrRelIso", "userFloat('deltaBetaCorrRelIso')"],
            ]
            )
        )
)

process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
        collections = cms.untracked.VPSet(treeCollection("goodSignalElectrons", 1,
            [
                ["Pt", "pt"],
                ["Eta", "eta"],
                ["Phi", "phi"],
                ["rhoCorrRelIso", "userFloat('rhoCorrRelIso')"],
            ]
            )
        )
)

process.treesDouble = cms.EDAnalyzer("DoubleTreemakerAnalyzer",
    collections = cms.VInputTag(
        cms.InputTag("cosThetaProducerEle", "cosThetaLightJet", "STPOLSEL2"),
        cms.InputTag("cosThetaProducerMu", "cosThetaLightJet", "STPOLSEL2"),
        cms.InputTag("muAndMETMT", "", "STPOLSEL2"),
        cms.InputTag("kt6PFJets", "rho", "RECO")
    )
)
process.treeSequence = cms.Sequence(process.treesMu*process.treesEle*process.treesDouble)

process.efficiencyAnalyzerMu = cms.EDAnalyzer('EfficiencyAnalyzer'
, histogrammableCounters = cms.untracked.vstring(["muPath"])
, muPath = cms.untracked.vstring([
    "singleTopPathStep1MuPreCount",
    "singleTopPathStep1MuPostCount",
    "muPathPreCount",
    "muPathStepHLTsyncPostCount",
    "muPathOneIsoMuPostCount",
    "muPathLooseMuVetoMuPostCount",
    "muPathLooseEleVetoMuPostCount",
    "muPathNJetsPostCount",
    "muPathHasMuMETMTPostCount",
    "muPathMBTagsPostCount"
    ]
))
process.efficiencyAnalyzerEle = cms.EDAnalyzer('EfficiencyAnalyzer'
, histogrammableCounters = cms.untracked.vstring(["elePath"])
, elePath = cms.untracked.vstring([
    "singleTopPathStep1ElePreCount",
    "singleTopPathStep1ElePostCount",
    "elePathPreCount",
    #"elePathStepHLTsyncPostCount",
    "elePathOneIsoElePostCount",
    "elePathLooseEleVetoElePostCount",
    "elePathLooseMuVetoElePostCount",
    "elePathNJetsPostCount",
    "elePathHasMETPostCount",
    "elePathMBTagsPostCount"
    ]
))

#-----------------------------------------------
# Paths
#-----------------------------------------------
from HLTrigger.HLTfilters.hltHighLevel_cfi import *

process.stepHLTsync = hltHighLevel.clone(
  TriggerResultsTag = "TriggerResults::HLT"
, HLTPaths = [
    #"HLT_IsoMu24_eta2p1_v11"
    #"HLT_IsoMu17_eta2p1_TriCentralPFNoPUJet30_30_20_v1"
    "HLT_IsoMu24_eta2p1_v13"
  ]
, andOr = True
)

process.goodSignalLeptons = cms.EDProducer(
    'CandRefCombiner',
    sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
    minOut=cms.untracked.uint32(1),
    maxOut=cms.untracked.uint32(1),
)

process.recoNu = cms.EDProducer(
    #'CompositeCandCollectionCombiner',
    'CandRefCombiner',
    sources=cms.untracked.vstring(["recoNuProducerEle", "recoNuProducerMu"]),
    minOut=cms.untracked.uint32(1),
    maxOut=cms.untracked.uint32(1),
)

process.recoTopEle = cms.EDProducer('SimpleCompositeCandProducer',
    sources=cms.VInputTag(["recoNuProducerEle", "bTagsTCHPtight", "goodSignalElectrons"])
)

process.recoTopMu = cms.EDProducer('SimpleCompositeCandProducer',
    sources=cms.VInputTag(["recoNuProducerMu", "bTagsTCHPtight", "goodSignalMuons"])
)

process.cosThetaProducerEle = cms.EDProducer('CosThetaProducer',
    topSrc=cms.InputTag("recoTopEle"),
    jetSrc=cms.InputTag("untaggedTCHPtight"),
    leptonSrc=cms.InputTag("goodSignalLeptons")
)

process.cosThetaProducerMu = cms.EDProducer('CosThetaProducer',
    topSrc=cms.InputTag("recoTopMu"),
    jetSrc=cms.InputTag("untaggedTCHPtight"),
    leptonSrc=cms.InputTag("goodSignalLeptons")
)

# process.recoTop = cms.EDProducer(
#     'CompositeCandCollectionCombiner',
#     sources=cms.untracked.vstring(["topsFromMu", "topsFromEle"]),
#     minOut=cms.untracked.uint32(1),
#     maxOut=cms.untracked.uint32(1),
# )

# process.nuAnalyzer = cms.EDAnalyzer(
#   'SimpleEventAnalyzer',
#   interestingCollection=cms.untracked.string("recoNu")
# )

process.muPathPreCount = cms.EDProducer("EventCountProducer")
process.muPath = cms.Path(
    process.muonsWithIso *
    process.elesWithIso *
    process.muPathPreCount *
    process.stepHLTsync *
    process.goodSignalMuons *
    process.goodQCDMuons *
    process.looseVetoMuons *
    process.oneIsoMu *
    process.looseMuVetoMu *
    process.looseVetoElectrons *
    process.looseEleVetoMu *
    process.noPUJets *
    process.smearedJets *
    process.goodJets *
    process.nJets *
    process.muAndMETMT *
    process.hasMuMETMT *
    process.goodSignalLeptons *
    process.recoNuProducerMu *
    process.recoNu *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.untaggedTCHPtight *
    process.mBTags *
    #process.topsFromMu *
    process.recoTopMu *
    process.cosThetaProducerMu *
    process.treeSequence *
    process.efficiencyAnalyzerMu
    #process.nuAnalyzer
)
countAfter(process, process.muPath,
    [
    "stepHLTsync",
    "oneIsoMu",
    "looseMuVetoMu",
    "looseEleVetoMu",
    "hasMuMETMT",
    "nJets",
    "mBTags"
    ]
)

process.elePathPreCount = cms.EDProducer("EventCountProducer")
process.elePath = cms.Path(
    process.muonsWithIso *
    process.elesWithIso *
    process.elePathPreCount *
    #process.stepHLTsync *
    process.goodSignalElectrons *
    process.goodQCDElectrons *
    process.looseVetoElectrons *
    process.oneIsoEle *
    process.looseEleVetoEle *
    process.looseVetoMuons *
    process.looseMuVetoEle *
    process.noPUJets *
    process.smearedJets *
    process.goodJets *
    process.nJets *
    process.goodMETs *
    process.hasMET *
    process.goodSignalLeptons *
    process.recoNuProducerEle *
    process.recoNu *
    process.bTagsCSVmedium *
    process.bTagsCSVtight *
    process.bTagsTCHPtight *
    process.untaggedTCHPtight *
    process.mBTags *
    #process.topsFromEle *
    process.recoTopEle *
    process.cosThetaProducerEle *
    process.treeSequence *
    process.efficiencyAnalyzerEle
    #process.nuAnalyzer
)
countAfter(process, process.elePath,
    [
    #"stepHLTsync",
    "oneIsoEle",
    "looseEleVetoEle",
    "looseMuVetoEle",
    "hasMET",
    "nJets",
    "mBTags"
    ]
)


#-----------------------------------------------
# Outpath
#-----------------------------------------------

process.out = cms.OutputModule("PoolOutputModule",
    fileName=cms.untracked.string('out_step2.root'),
     SelectEvents=cms.untracked.PSet(
         SelectEvents=cms.vstring(['muPath', 'elePath'])
     ),
    outputCommands=cms.untracked.vstring(
        'keep *',
        'drop patElectrons_looseVetoElectrons__PAT',
        'drop patMuons_looseVetoMuons__PAT',
        'drop *_recoNuProducerEle_*_*',
        'drop *_recoNuProducerMu_*_*',
        #'drop *_topsFromMu_*_*',
        #'drop *_topsFromEle_*_*',
    )
)
process.outpath = cms.EndPath(process.out)

#-----------------------------------------------
#
#-----------------------------------------------

#Command-line arguments
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string(process.out.fileName.value().replace(".root", "_trees.root")),
)

