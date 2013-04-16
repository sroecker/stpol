#Compile with
#$ scram b -f SingleTopPolarization/Analysis
#Output will be in $CMSSW_DIR/bin/
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
print "Input files: %s" % input_files
print "Output file: %s" %  outfile

process.fwliteOutput = cms.PSet(
    fileName  = cms.string(outfile),
)

process.muonCuts = cms.PSet(
    cutOnIso  = cms.bool(False),
    reverseIsoCut  = cms.bool(False),
    requireOneMuon  = cms.bool(True),
    isoCut  = cms.double(0.12),
    muonPtSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muonRelIsoSrc  = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    muonCountSrc  = cms.InputTag("muonCount"),
    doVetoLeptonCut = cms.bool(True),
    vetoMuCountSrc = cms.InputTag("looseVetoMuCount"),
    vetoEleCountSrc = cms.InputTag("looseVetoEleCount"),
)

process.eleCuts = cms.PSet(
)

process.jetCuts = cms.PSet(
    cutOnNJets  = cms.bool(False),
    cutOnNTags  = cms.bool(False),
    applyRmsLj  = cms.bool(False),
    applyEtaLj  = cms.bool(False),

    goodJetsCountSrc = cms.InputTag("goodJetCount"),
    bTagJetsCountSrc = cms.InputTag("bJetCount"),

    rmsMax = cms.double(0.025),

    nJetsMin = cms.int32(2),
    nJetsMax = cms.int32(2),

    nTagsMin = cms.int32(0),
    nTagsMax = cms.int32(9),

    goodJetsPtSrc = cms.InputTag("goodJetsNTupleProducer", "Pt"),
    goodJetsEtaSrc = cms.InputTag("goodJetsNTupleProducer", "Eta"),

    lightJetEtaSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    lightJetBdiscrSrc = cms.InputTag("lowestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    lightJetPtSrc = cms.InputTag("lowestBTagJetNTupleProducer", "Pt"),
    lightJetRmsSrc = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),

    bJetEtaSrc = cms.InputTag("highestBTagJetNTupleProducer", "Eta"),
    bJetBdiscrSrc = cms.InputTag("highestBTagJetNTupleProducer", "bDiscriminatorTCHP"),
    bJetPtSrc = cms.InputTag("highestBTagJetNTupleProducer", "Pt"),
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
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight")
)

process.mtMuCuts = cms.PSet(
    mtMuSrc = cms.InputTag("muAndMETMT"),
    doMTCut = cms.bool(False),
    minVal = cms.double(40)
)

process.finalVars = cms.PSet(
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("offlinePVCount"),
    scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors")
)

process.lumiBlockCounters = cms.PSet(
    totalPATProcessedCountSrc = cms.InputTag("singleTopPathStep1MuPreCount")
)

process.genParticles = cms.PSet(
    doGenParticles = cms.bool(isMC),
    trueBJetCountSrc = cms.InputTag("trueBJetCount"),
    trueCJetCountSrc = cms.InputTag("trueCJetCount"),
    trueLJetCountSrc = cms.InputTag("trueLJetCount"),
    trueBJetTaggedCountSrc = cms.InputTag("btaggedTrueBJetCount"),
    trueCJetTaggedCountSrc = cms.InputTag("btaggedTrueCJetCount"),
    trueLJetTaggedCountSrc = cms.InputTag("btaggedTrueLJetCount"),
)
