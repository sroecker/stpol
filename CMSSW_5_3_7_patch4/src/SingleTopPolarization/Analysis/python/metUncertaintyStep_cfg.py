import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

options = VarParsing('analysis')
options.register ('globalTag', "START53_V15::All",
          VarParsing.multiplicity.singleton,
          VarParsing.varType.string,
          "Global tag"
)
options.parseArguments()

process = cms.Process("STPOLSEL1B")
process.load("Configuration.Geometry.GeometryIdeal_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
from Configuration.AlCa.autoCond import autoCond
process.GlobalTag.globaltag = cms.string(options.globalTag)
process.load("Configuration.StandardSequences.MagneticField_cff")

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames=cms.untracked.vstring("")
)
process.source.fileNames = cms.untracked.vstring(options.inputFiles)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(options.maxEvents))

#Embed the reference to the original jet in the jets, which is constant during the propagation
process.patJetsWithOwnRef = cms.EDProducer('PatObjectOwnRefProducer<pat::Jet>',
    src=cms.InputTag("selectedPatJets")
)
from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
runMEtUncertainties(process,
     electronCollection=cms.InputTag("electronsWithID"),
     photonCollection=None,
     muonCollection=cms.InputTag("muonsWithID"),
     tauCollection="", # "" means emtpy, None means cleanPatTaus
     jetCollection=cms.InputTag("patJetsWithOwnRef"),
     addToPatDefaultSequence=False
)
process.metUncertaintyPath = cms.Path(
    process.patJetsWithOwnRef *
    process.metUncertaintySequence
)

process.out = cms.OutputModule("PoolOutputModule",
    dropMetaData=cms.untracked.string("ALL"),
    fileName=cms.untracked.string('out_step1_1.root'),
     SelectEvents=cms.untracked.PSet(
         SelectEvents=cms.vstring([])
     ),
    outputCommands=cms.untracked.vstring(
        #'drop *',
        'keep *',
        'drop recoPFCandidates_*_pfCandidates_PAT',
        'drop recoPFMETs_pfMET__PAT',
        'drop recoPFMETs_pfMet__RECO',
        'drop recoGenMETs_genMetTrue__SIM',
        'drop recoPFCandidates_particleFlow__RECO',
        'drop recoConversions_allConversions__RECO',
        'drop recoVertexCompositeCandidates_generalV0Candidates_*_RECO',
        'drop recoTracks_generalTracks__RECO',
        'drop recoBeamSpot_offlineBeamSpot__RECO',
        'drop recoMuons_muons__RECO',
    )
)
process.out.fileName = cms.untracked.string(options.outputFile)
process.outpath = cms.EndPath(process.out)
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))
