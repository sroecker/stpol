#Compile with
#$ scram b -f SingleTopPolarization/Analysis
#Output will be in $CMSSW_DIR/bin/

#Note - this is a generic example file, rather than changing it, make your own based on it, using the cuts you need
import FWCore.ParameterSet.Config as cms
import sys
import pdb
import optparse
import random
import string
import os

#outfile = "step3_out_%s.root" % (''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(6)))
if "STPOL_STEP3_OUTPUTFILE" in os.environ.keys():
    outfile = os.environ['STPOL_STEP3_OUTPUTFILE']
else:
    outfile = "out_step3.root"
if "STPOL_ISMC" in os.environ.keys():
    isMC_env = os.environ["STPOL_ISMC"]
    if isMC_env.lower() == "true":
        isMC = True
    elif isMC_env.lower() == "false":
        isMC = False
    else:
        raise ValueError("STPOL_ISMC must be true/false")
else:
    isMC = True
print "isMC = %s" % isMC

#read input files from stdin
input_files = []
print "Waiting for input files over stdin..."
for line in sys.stdin.readlines():
    input_files.append(line.strip())

#parser = optparse.OptionParser()
#parser.add_option("--outfile", dest="outfile", type="string")
#options, args = parser.parse_args()

process = cms.Process("STPOLSEL3")
#process.load("FWCore.MessageLogger.MessageLogger_cfi")
#process.MessageLogger.cerr.FwkReport.reportEvery = 1000
#process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring(input_files),
    maxEvents   = cms.int32(-1),
    outputEvery = cms.uint32(10000),
)
print "Input files:"
for fi in input_files:
    print "\t",fi
print "Output file: %s" %  outfile


doControlVars = True
process.fwliteOutput = cms.PSet(
    fileName  = cms.string(outfile),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(False),
    doControlVars  = cms.bool(doControlVars),
    reverseIsoCut  = cms.bool(False),
    requireOneMuon  = cms.bool(True),
    isoCut  = cms.double(0.12),

    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    eleCountSrc  = cms.InputTag("electronCount"),

    doVetoLeptonCut = cms.bool(True),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),

    muonDbSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "db"),
    muonDzSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "dz"),
    muonNormChi2Src = cms.InputTag("goodSignalMuonsNTupleProducer", "normChi2"),
    muonChargeSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "Charge"),

    muonGTrackHitsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "globalTrackhitPatternnumberOfValidMuonHits"),
    muonITrackHitsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "innerTrackhitPatternnumberOfValidPixelHits"),
    muonStationsSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "numberOfMatchedStations"),
    muonLayersSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "trackhitPatterntrackerLayersWithMeasurement"),
    muonMotherPdgIdSrc = cms.InputTag("goodSignalMuonsNTupleProducer", "motherGenPdgId"),

)

process.eleCuts = cms.PSet(
    requireOneElectron = cms.bool(False),
    eleCountSrc  = cms.InputTag("electronCount"),
    muonCountSrc = cms.InputTag("muonCount"),
    electronRelIsoSrc = cms.InputTag("goodSignalElectronsNTupleProducer","relIso"),
    electronMvaSrc = cms.InputTag("goodSignalElectronsNTupleProducer","mvaID"),
    electronPtSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Pt"),
    electronChargeSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "Charge"),
    electronMotherPdgIdSrc = cms.InputTag("goodSignalElectronsNTupleProducer", "motherGenPdgId"),
    doVetoLeptonCut = cms.bool(True),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
)

process.jetCuts = cms.PSet(
    cutOnNJets  = cms.bool(False),
    applyRmsLj  = cms.bool(False),
    applyEtaLj  = cms.bool(False),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),
    etaMin = cms.double(0.0),

    nJetsMin = cms.int32(0),
    nJetsMax = cms.int32(4),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
    lightJetDeltaRSrc = cms.InputTag("lowestBTagJetNTupleProducer", "deltaR"),

    #bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    #bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    #bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
)

process.bTagCuts = cms.PSet(
    cutOnNTags  = cms.bool(False),

    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    nTagsMin = cms.int32(0),
    nTagsMax = cms.int32(2),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
    bJetDeltaRSrc = cms.InputTag("highestBTagJetNTupleProducer", "deltaR")
)

process.topCuts = cms.PSet(
        applyMassCut = cms.bool(False),
        signalRegion = cms.bool(True),
        signalRegionMassLow = cms.double(130),
        signalRegionMassHigh = cms.double(220),
        topMassSrc = cms.InputTag("recoTopNTupleProducer", "Mass")
)

process.weights = cms.PSet(
    doWeights = cms.bool(isMC),
    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNJMT", "bTagWeight"),
    puWeightSrc = cms.InputTag("puWeightProducer", "PUWeightNtrue"),
    muonIDWeightSrc = cms.InputTag("muonWeightsProducer", "muonIDWeight"),
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight"),
    electronIDWeightSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeight"),
    electronTriggerWeightSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeight")
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    metSrc = cms.InputTag("patMETNTupleProducer", "Pt"),
    doMTCut = cms.bool(False),
    minVal = cms.double(40)
)

#The versions should be specified explicitly at the moment
process.HLT = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        #"HLT_IsoMu17_eta2p1_TriCentralPFNoPUJet50_40_30_v1",
        #"HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_TriCentralPFNoPUJet50_40_30_v5",
        #"HLT_Ele25_CaloIdVT_CaloIsoVL_TrkIdVL_TrkIsoT_TriCentralPFNoPUJet50_40_30_v1",
        "HLT_IsoMu24_eta2p1_v11",
        "HLT_IsoMu24_eta2p1_v12",
        "HLT_IsoMu24_eta2p1_v13",
        "HLT_IsoMu24_eta2p1_v14",
        "HLT_IsoMu24_eta2p1_v15",
        "HLT_IsoMu24_eta2p1_v17",
        "HLT_IsoMu24_eta2p1_v16"
    ]),
    doCutOnHLT = cms.bool(True)
)

process.HLTele = cms.PSet(
    hltSrc = cms.InputTag("TriggerResults", "", "HLT"),
    hltNames = cms.vstring([
        "HLT_Ele27_WP80_v8",
        "HLT_Ele27_WP80_v9",
        "HLT_Ele27_WP80_v10",
        "HLT_Ele27_WP80_v11",
        ]),
    doCutOnHLT = cms.bool(False)
)

process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("offlinePVCount"),
    #scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors")

    #PDF stuff
    addPDFInfo = cms.bool(False),
    scalePDFSrc = cms.InputTag("PDFweights", "scalePDF"),
	x1Src = cms.InputTag("PDFweights", "x1"),
	x2Src = cms.InputTag("PDFweights", "x2"),
	id1Src = cms.InputTag("PDFweights", "id1"),
	id2Src = cms.InputTag("PDFweights", "id2"),

    #PDFSets = cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
	PDFSets	= cms.vstring('NNPDF21_100.LHgrid','CT10.LHgrid','MSTW2008nlo68cl.LHgrid'),
)

process.lumiBlockCounters = cms.PSet(
    totalPATProcessedCountSrc = cms.InputTag("singleTopPathStep1MuPreCount")
)

process.genParticles = cms.PSet(
    doGenParticles = cms.bool(isMC and doControlVars),
    trueBJetCountSrc = cms.InputTag("trueBJetCount"),
    trueCJetCountSrc = cms.InputTag("trueCJetCount"),
    trueLJetCountSrc = cms.InputTag("trueLJetCount"),
    trueBJetTaggedCountSrc = cms.InputTag("btaggedTrueBJetCount"),
    trueCJetTaggedCountSrc = cms.InputTag("btaggedTrueCJetCount"),
    trueLJetTaggedCountSrc = cms.InputTag("btaggedTrueLJetCount"),
    trueCosThetaSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),
    trueLeptonPdgIdSrc = cms.InputTag("genParticleSelector", "trueLeptonPdgId"),
	requireGenMuon  = cms.bool(False)
)

doSync = False
if doSync:
    process.muonCuts.requireOneMuon = True
    process.muonCuts.doVetoLeptonCut = True
    process.jetCuts.cutOnNJets = True
    process.jetCuts.nJetsMin = 2
    process.jetCuts.nJetsMax = 2

    process.bTagCuts.cutOnNTags = True
    process.bTagCuts.nTagsMin = 1
    process.bTagCuts.nTagsMax = 1

    process.mtMuCuts.doMTCut = True
    process.mtMuCuts.minVal = 50
