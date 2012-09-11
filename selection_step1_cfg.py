#from Configuration.StandardSequences.Geometry_cff import *
from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
import FWCore.ParameterSet.Config as cms

## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *

postfix = ""

usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=True,
          postfix=postfix,
          jetCorrections=(
              'AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute']),
          pvCollection=cms.InputTag('goodOfflinePrimaryVertices'))


getattr(process, "pfPileUp" + postfix).checkClosestZVertex = False

process.patMuons.usePV = False
process.pfPileUp.Enable = True
process.pfPileUp.checkClosestZVertex = False

#process.pfPileUp.Enable = True

#-------------------------------------------------
# selection step 1: trigger
# Based on
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel#Triggers
# Section Monte Carlo Summer12 with CMSSW_5_2_X and GT START52_V9
#-------------------------------------------------

from HLTrigger.HLTfilters.hltHighLevel_cfi import *

process.step1_HLT = hltHighLevel.clone(TriggerResultsTag="TriggerResults::HLT", HLTPaths=["HLT_IsoMu17_eta2p1_TriCentralPFJet30_v2", "HLT_IsoMu20_eta2p1_TriCentralPFNoPUJet30_v2"], andOr=True)

#-------------------------------------------------
# selection step 2: vertex filter
#-------------------------------------------------

process.goodOfflinePrimaryVertices = cms.EDFilter(
                                                  "PrimaryVertexObjectFilter"
                                                  , filterParams = cms.PSet(
                                                                            minNdof = cms.double(4.0)
                                                                            , maxZ = cms.double(24.0)
                                                                            , maxRho = cms.double(2.0)
                                                  )
                                                  , filter = cms.bool(True)
                                                  , src = cms.InputTag('offlinePrimaryVertices')
)

process.processedEventCounter = cms.EDProducer("EventCountProducer")
process.muCounter = cms.EDProducer("EventCountProducer")

#-------------------------------------------------
# Muons
#-------------------------------------------------

goodMuonCut = 'isPFMuon'                                                                           # general reconstruction property
goodMuonCut += ' && isGlobalMuon'                                                                   # general reconstruction property
goodMuonCut += ' && pt > 26.'                                                                       # transverse momentum
goodMuonCut += ' && abs(eta) < 2.1'                                                                 # pseudo-rapisity range
goodMuonCut += ' && globalTrack.normalizedChi2 < 10.'                                               # muon ID: 'isGlobalMuonPromptTight'
goodMuonCut += ' && track.hitPattern.trackerLayersWithMeasurement > 5'                              # muon ID: 'isGlobalMuonPromptTight'
goodMuonCut += ' && globalTrack.hitPattern.numberOfValidMuonHits > 0'                               # muon ID: 'isGlobalMuonPromptTight'
goodMuonCut += ' && abs(dB) < 0.2'                                                                  # 2-dim impact parameter with respect to beam spot (s. "PAT muon configuration" above)
goodMuonCut += ' && innerTrack.hitPattern.numberOfValidPixelHits > 0'                               # tracker reconstruction
goodMuonCut += ' && numberOfMatchedStations > 1'                                                    # muon chamber reconstruction
#signalMuonCut += ' && (chargedHadronIso+max(0.0,neutralHadronIso+photonIso-0.5*puChargedHadronIso))/pt < 0.12' # Delta beta corrections (factor 0.5)

#goodSignalMuonCut = goodMuonCut + ' && (chargedHadronIso+max(0.0,neutralHadronIso+photonIso-0.5*puChargedHadronIso))/pt < 0.12'
#goodQCDMuonCut = goodMuonCut + '&& (chargedHadronIso+max(0.0,neutralHadronIso+photonIso-0.5*puChargedHadronIso))/pt < 0.5\
#                                  && (chargedHadronIso+max(0.0,neutralHadronIso+photonIso-0.5*puChargedHadronIso))/pt > 0.3'


process.pfIsolatedMuons.doDeltaBetaCorrection = False
process.pfIsolatedMuons.isolationCut = 1.0  # Deliberately put a large isolation cut

process.goodMuons = process.selectedPatMuons.clone(
  src=cms.InputTag("selectedPatMuons"), cut=goodMuonCut
)

#process.patMuons.userData.userFunctions = cms.vstring('((chargedHadronIso()+max(0.0,neutralHadronIso()+photonIso()-0.5*puChargedHadronIso()))/pt())')
#process.patMuons.userData.userFunctionLabels = cms.vstring('pfRelIso04')

#process.goodSignalMuons = process.selectedPatMuons.clone(
#  src=cms.InputTag("goodMuons"), cut=goodSignalMuonCut
#)
#
#process.goodQCDMuons = process.selectedPatMuons.clone(
#  src=cms.InputTag("goodMuons"), cut=goodQCDMuonCut
#)

#-------------------------------------------------
# Electrons
#-------------------------------------------------

#useGsfElectrons(process, postfix=postfix)  # , dR="03")
#process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
#process.mvaID = cms.Sequence(process.mvaTrigV0 + process.mvaNonTrigV0)
#process.patElectrons.electronIDSources.mvaTrigV0 = cms.InputTag("mvaTrigV0")
#process.patElectrons.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0")
#process.patPF2PATSequence.replace(process.patElectrons, process.mvaID * process.patElectrons)

signalElectronCut = "pt>30"
signalElectronCut += "&& abs(eta)<2.5"
signalElectronCut += "&& !(1.4442 < abs(superCluster.eta) < 1.5660)"
signalElectronCut += "&& passConversionVeto()"
#signalElectronCut += "&& 0.0<electronID('mvaTrigV0')<1.0"
#signalElectronCut += "&& (chargedHadronIso+max(0.0,neutralHadronIso+photonIso-0.5*puChargedHadronIso))/pt < 0.20"

process.goodElectrons = process.selectedPatElectrons.clone(
  src=cms.InputTag("selectedPatElectrons"), cut=signalElectronCut
)

#from PhysicsTools.PatAlgos.selectionLayer1.muonCountFilter_cfi import *
# process.step_isoMu1 = countPatMuons.clone(src = 'intermediatePatMuons',
# minNumber = 1, maxNumber = 1)

#-------------------------------------------------
# Electrons
#-------------------------------------------------

jetCut = 'pt > 20.'                                                  # transverse momentum
jetCut += ' && abs(eta) < 5.0'                                        # pseudo-rapidity range
jetCut += ' && numberOfDaughters > 1'                                 # PF jet ID:
jetCut += ' && neutralHadronEnergyFraction < 0.99'                    # PF jet ID:
jetCut += ' && neutralEmEnergyFraction < 0.99'                        # PF jet ID:
jetCut += ' && (chargedEmEnergyFraction < 0.99 || abs(eta) >= 2.4)'   # PF jet ID:
jetCut += ' && (chargedHadronEnergyFraction > 0. || abs(eta) >= 2.4)'  # PF jet ID:
jetCut += ' && (chargedMultiplicity > 0 || abs(eta) >= 2.4)'          # PF jet ID:

from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *

process.pfNoTau.enable = False

process.goodJets = process.selectedPatJets.clone(
    src='selectedPatJets' + postfix, cut= jetCut)

process.step_isoMu1 = process.countPatMuons.clone(src = 'goodMuons', minNumber = 1, maxNumber = 99)
# process.step_Jets = process.countPatJets.clone(src = 'goodJets', minNumber =
# 2, maxNumber = 2)

#-------------------------------------------------
# Paths
#-------------------------------------------------

#Currently, all in one path
#TODO: split muon and electron paths according to HLT
process.singleTopPath_step1 = cms.Path(#process.step1_HLT #If the HLT is before the PAT sequence, only the events passing the HLT will go to the (slow) PAT sequence
                                       process.processedEventCounter
                                     * process.goodOfflinePrimaryVertices
                                     * process.patPF2PATSequence
                                     * process.goodMuons
#                                     * process.goodSignalMuons
#                                     * process.goodQCDMuons
                                     * process.goodElectrons
                                     * process.goodJets
                                     * process.step_isoMu1
                                     * process.muCounter
#                                     * process.step_Jets
)


#from PhysicsTools.PatAlgos.patEventContent_cff import patEventContentNoCleaning
keepAll = False
if keepAll:
    process.out.outputCommands = cms.untracked.vstring('keep *')
else:
    process.out.outputCommands = cms.untracked.vstring([
          'drop *',
          'keep edmMergeableCounter_*_*_*',
          'keep edmTriggerResults_TriggerResults__HLT',
    #      'keep patElectrons_selectedPatElectrons__PAT',
    #      'keep patMuons_selectedPatMuons__PAT',
    #      'keep patJets_selectedPatJets__PAT',
    #      'keep patTaus_selectedPatTaus__PAT',
          'keep patJets_goodJets__PAT',
          'keep recoGenJets_goodJets_genJets_PAT',
    #      'keep patMuons_goodSignalMuons__PAT',
    #      'keep patMuons_goodQCDMuons__PAT',
          'keep patMuons_goodMuons__PAT',
          'keep patElectrons_goodElectrons__PAT',
          ])  # + patEventContentNoCleaning)

process.out.SelectEvents.SelectEvents = ["singleTopPath_step1"]
process.GlobalTag.globaltag = cms.string('START52_V9B::All')

inFileName= "file:/home/joosep/singletop/FEFF01BD-87DC-E111-BC9E-003048678F8E.root"
process.source.fileNames = cms.untracked.vstring(inFileName)
process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(100))
