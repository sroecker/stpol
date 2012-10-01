#from Configuration.StandardSequences.Geometry_cff import *
from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
import FWCore.ParameterSet.Config as cms

## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger = cms.Service("MessageLogger",
       destinations   = cms.untracked.vstring(
                                              'cout',
                                             'debug'
                    ),
       debugModules   = cms.untracked.vstring('muonsWithID'),
       debug       = cms.untracked.PSet(
                       threshold = cms.untracked.string('DEBUG') 
        ),
       cout       = cms.untracked.PSet(
                       threshold = cms.untracked.string('ERROR') 
        ),
)

#VarParsing
from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
enableCommandLineArguments(process)

#Should do pre-PFBRECO-skimming (discard uninteresting events)
doSkimming = True

#Should slim (drop the unnecessary collections) the output?
doSlimming = True

postfix = ""

usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=True, postfix=postfix,
  jetCorrections=('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute']),
  pvCollection=cms.InputTag('goodOfflinePrimaryVertices')
)


getattr(process, "pfPileUp" + postfix).checkClosestZVertex = False

process.patMuons.usePV = False
process.pfPileUp.Enable = True
process.pfPileUp.checkClosestZVertex = False

#process.pfPileUp.Enable = True

#-----------------------------------------------
# selection step 0: initial skim filter (reco filter)
#-----------------------------------------------

#DEPRECATED
# process.initialSkimFilter = cms.EDFilter("SingleTopRecoFilter",
#   minMuons = cms.untracked.int32(1),
#   minJets = cms.untracked.int32(2),
#   minMuonPt = cms.untracked.double(25.0),
#   minJetPt = cms.untracked.double(20.0),
#   maxMuonEta = cms.untracked.double(2.1),
#   maxMuonRelIso = cms.untracked.double(10000.0),
#   maxJetEta = cms.untracked.double(5.0)
#   )


#-------------------------------------------------
# selection step 1: trigger
# Based on
# https://twiki.cern.ch/twiki/bin/view/CMS/TWikiTopRefEventSel#Triggers
# Section Monte Carlo Summer12 with CMSSW_5_2_X and GT START52_V9
#-------------------------------------------------

from HLTrigger.HLTfilters.hltHighLevel_cfi import *

process.step1_HLT = hltHighLevel.clone(
  TriggerResultsTag = "TriggerResults::HLT"
, HLTPaths = [
    "HLT_IsoMu17_eta2p1_TriCentralPFJet30_v2"
  , "HLT_IsoMu20_eta2p1_TriCentralPFNoPUJet30_v2"
  ]
, andOr = True
)

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


#-------------------------------------------------
# Muons
#-------------------------------------------------

process.pfIsolatedMuons.doDeltaBetaCorrection = False
process.pfIsolatedMuons.isolationCut = 100.0  # Deliberately put a large isolation cut

process.muonsWithIso = cms.EDProducer(
  'MuonIsolationProducer',
  leptonSrc = cms.InputTag("selectedPatMuons" + postfix),
  rhoSrc = cms.InputTag("kt6PFJets", "rho")
)

process.muonsWithID = cms.EDProducer(
  'MuonIDProducer',
  muonSrc = cms.InputTag("muonsWithIso"),
  primaryVertexSource = cms.InputTag("offlinePrimaryVertices")
)

# process.muSequence = cms.Sequence(
#   process.goodSignalMuons
#   * process.goodQCDMuons
#   * process.looseVetoMuons
# )

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
# Implemented as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=208765
#-------------------------------------------------

useGsfElectrons(process, postfix=postfix)
process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
process.mvaID = cms.Sequence(process.mvaTrigV0 + process.mvaNonTrigV0)
process.patElectrons.electronIDSources.mvaTrigV0 = cms.InputTag("mvaTrigV0")
process.patElectrons.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0")
process.patPF2PATSequence.replace(process.patElectrons, process.mvaID * process.patElectrons)

process.elesWithIso = cms.EDProducer(
  'ElectronIsolationProducer',
  leptonSrc = cms.InputTag("selectedPatElectrons" + postfix),
  rhoSrc = cms.InputTag("kt6PFJets", "rho")
)

#-------------------------------------------------
# Jets
#-------------------------------------------------

from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *
process.pfNoTau.enable = False

#-------------------------------------------------
# Object counters
#-------------------------------------------------

#from PhysicsTools.PatAlgos.selectionLayer1.muonCountFilter_cfi import *
#process.step_isoMu1 = process.countPatMuons.clone(src = 'goodMuons', minNumber = 1, maxNumber = 99)
# process.step_Jets = process.countPatJets.clone(src = 'goodJets', minNumber =
# 2, maxNumber = 2)

#-------------------------------------------------
# Paths
#-------------------------------------------------

process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatElectrons) + 1, process.elesWithIso)
process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatMuons) + 1, process.muonsWithIso*process.muonsWithID)

#Need separate paths because of skimming
process.singleTopPathStep1Mu = cms.Path(
  process.goodOfflinePrimaryVertices
  * process.patPF2PATSequence
)

process.singleTopPathStep1Ele = cms.Path(
  process.goodOfflinePrimaryVertices
  * process.patPF2PATSequence
)

#-----------------------------------------------
# Skimming
#-----------------------------------------------

#Throw away events before particle flow?
if doSkimming:
    from SingleTopPolarization.Analysis.step_eventSkim_cfg import skimFilters
    skimFilters(process)
    process.singleTopPathStep1Mu.insert(0, process.muonSkim)
    process.singleTopPathStep1Ele.insert(0, process.electronSkim)

#-----------------------------------------------
# Skim efficiency counters
#-----------------------------------------------

from SingleTopPolarization.Analysis.eventCounting import *

#count all processed events
countProcessed(process) 

#count events passing mu and ele paths
countInSequence(process, process.singleTopPathStep1Mu)
countInSequence(process, process.singleTopPathStep1Ele)

#-----------------------------------------------
# Slimming
#-----------------------------------------------

if not doSlimming:
    process.out.outputCommands = cms.untracked.vstring('keep *')
else:
    process.out.outputCommands = cms.untracked.vstring([
        'drop *',

        'keep edmMergeableCounter_*_*_*', # Keep the lumi-block counter information
        'keep edmTriggerResults_TriggerResults__HLT', #Keep the trigger results
        'keep recoGenParticles_genParticles__SIM', #keep all the genParticles
        'keep recoVertexs_offlinePrimaryVertices__RECO', #keep the offline PV-s

    #      'keep patElectrons_selectedPatElectrons__PAT',
    #      'keep patMuons_selectedPatMuons__PAT',
    #      'keep patJets_selectedPatJets__PAT',
    #      'keep patTaus_selectedPatTaus__PAT',

        # Jets
        'keep patJets_selectedPatJets__PAT',
        'keep double_*_rho_RECO', #For rho-corr rel iso
        'keep recoGenJets_selectedPatJets_genJets_PAT', #For Jet MC smearing we need to keep the genJets

        # Muons
        'keep patMuons_muonsWithID__PAT',

        # Electrons
        'keep patElectrons_elesWithIso__PAT',

        'keep patMETs_patMETs__PAT'
    ])

#Keep events that pass either the muon OR the electron path
process.out.SelectEvents = cms.untracked.PSet(
  SelectEvents = cms.vstring(
    ["singleTopPathStep1Mu", "singleTopPathStep1Ele"]
  )
)

process.GlobalTag.globaltag = cms.string('START52_V9B::All')
