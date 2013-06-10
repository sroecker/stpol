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

isMC = True

#read input files from stdin
input_files = []
print "Waiting for input files over stdin..."
for line in sys.stdin.readlines():
    input_files.append(line.strip())


process = cms.Process("STPOLSEL3")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring(input_files),
    maxEvents   = cms.int32(-1),
    outputEvery = cms.uint32(1000000),
)
print "Input files: %s" % input_files
print "Output file: %s" %  outfile

process.fwliteOutput = cms.PSet(
    fileName  = cms.string(outfile),
)

process.muonCuts = cms.PSet(
    muonPtSrc  = cms.InputTag("trueLeptonNTupleProducer", "Pt")    
)

process.eleCuts = cms.PSet(
    electronPtSrc = cms.InputTag("trueLeptonNTupleProducer", "Pt")    
)

process.weights = cms.PSet(
    doWeights = cms.bool(True),
    bWeightNominalSrc = cms.InputTag("bTagWeightProducerNJMT", "bTagWeight"),
    puWeightSrc = cms.InputTag("puWeightProducer", "PUWeightNtrue"),

    muonIDWeightSrc = cms.InputTag("muonWeightsProducer", "muonIDWeight"),
    muonIsoWeightSrc = cms.InputTag("muonWeightsProducer", "muonIsoWeight"),
    muonTriggerWeightSrc = cms.InputTag("muonWeightsProducer", "muonTriggerWeight"),

    electronIDWeightSrc = cms.InputTag("electronWeightsProducer","electronIdIsoWeight"),
    electronTriggerWeightSrc = cms.InputTag("electronWeightsProducer","electronTriggerWeight")
)

process.finalVars = cms.PSet()
"""
    cosThetaSrc = cms.InputTag("cosTheta", "cosThetaLightJet"),
    nVerticesSrc = cms.InputTag("offlinePVCount"),
    scaleFactorsSrc = cms.InputTag("bTagWeightProducerNJMT", "scaleFactors")
)
"""
process.lumiBlockCounters = cms.PSet(
    totalPATProcessedCountSrc = cms.InputTag("singleTopPathStep1MuPreCount")
)

process.jetCuts = cms.PSet()

process.genParticles = cms.PSet(
    doGenParticles = cms.bool(True),
    trueBJetCountSrc = cms.InputTag("trueBJetCount"),
    trueCJetCountSrc = cms.InputTag("trueCJetCount"),
    trueLJetCountSrc = cms.InputTag("trueLJetCount"),
    trueBJetTaggedCountSrc = cms.InputTag("btaggedTrueBJetCount"),
    trueCJetTaggedCountSrc = cms.InputTag("btaggedTrueCJetCount"),
    trueLJetTaggedCountSrc = cms.InputTag("btaggedTrueLJetCount"),
    trueCosThetaSrc = cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),
    trueLeptonPdgIdSrc = cms.InputTag("genParticleSelector", "trueLeptonPdgId"),
    wJetsClassificationSrc = cms.InputTag("flavourAnalyzer", "simpleClass"),
	requireGenMuon  = cms.bool(False)
)

for k, v in process.__dict__.items():
    if isinstance(v, cms.PSet):
        print k, v
