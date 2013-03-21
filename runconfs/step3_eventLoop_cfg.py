#Compile with
#$ scram b -f SingleTopPolarization/Analysis
#Output will be in $CMSSW_DIR/bin/
import FWCore.ParameterSet.Config as cms

process = cms.Process("STPOLSEL3")
#process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring('/Users/joosep/Documents/stpol/T_t_merged.root'),
    maxEvents   = cms.int32(10000),
    outputEvery = cms.uint32(1000),
)

process.fwliteOutput = cms.PSet(
    fileName  = cms.string('stpol_step3.root'),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(False),
    reverseIsoCut  = cms.bool(False),
    isoCut  = cms.double(0.12),
    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
)

process.eleCuts = cms.PSet(
)

process.jetCuts = cms.PSet(
    cutOnNJets  = cms.bool(True),
    cutOnNTags  = cms.bool(True),
    applyRmsLj  = cms.bool(False),
    applyEtaLj  = cms.bool(False),
    
    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),
    
    rmsMax = cms.double(0.025),
    
    nJetsMin = cms.int32(2),
    nJetsMax = cms.int32(2),
    
    nTagsMin = cms.int32(1),
    nTagsMax = cms.int32(1),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),
    
    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminator"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
        
    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminator"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(True),
        signalRegion = cms.bool(True),
        signalRegionMassLow = cms.double(170-30),
        signalRegionMassHigh = cms.double(170+30),
        topMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass")
)

process.bWeights = cms.PSet(
    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNJMT", "bTagWeight")
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    minVal = cms.double(50)
)

process.cosTheta = cms.PSet(
    cosThetaSrc = cms.InputTag("cosThetaProducer", "cosTheta")
)
