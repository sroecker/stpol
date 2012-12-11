#from Configuration.StandardSequences.Geometry_cff import *
from Configuration.Geometry.GeometryIdeal_cff import *
from Configuration.StandardSequences.MagneticField_cff import *
from Configuration.StandardSequences.FrontierConditions_GlobalTag_cff import *
import FWCore.ParameterSet.Config as cms

## import skeleton process
from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.pfTools import *

from SingleTopPolarization.Analysis.eventCounting import *

#from HLTrigger.HLTfilters.hltHighLevel_cfi import *

from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *


def SingleTopStep1(
  process,
  isMC,
  doDebug=False, 
  doSkimming=True,
  doSlimming=True,
  doMuon=True,
  doElectron=True,
  onGrid=False,
  maxLeptonIso=0.2,
  globalTag="START53_V7F"
  ):

  if doDebug:
      process.load("FWCore.MessageLogger.MessageLogger_cfi")
      process.MessageLogger = cms.Service("MessageLogger",
             destinations=cms.untracked.vstring('cout', 'debug'),
             debugModules=cms.untracked.vstring('*'),
             cout=cms.untracked.PSet(threshold=cms.untracked.string('INFO')),
             debug=cms.untracked.PSet(threshold=cms.untracked.string('DEBUG')),
      )
  else:
      process.load("FWCore.MessageService.MessageLogger_cfi")

  postfix = ""

  usePF2PAT(process, runPF2PAT=True, jetAlgo='AK5', runOnMC=isMC, postfix=postfix,
    jetCorrections=('AK5PFchs', ['L1FastJet', 'L2Relative', 'L3Absolute']),
    pvCollection=cms.InputTag('goodOfflinePrimaryVertices'),
    #typeIMetCorrections = True #FIXME: Does this automatically add type1 corrections completely and consistently?
    typeIMetCorrections = False #Type1 MET now applied later using runMETUncertainties
  )
  
  # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCorPFnoPU2012
  process.pfPileUp.Enable = True
  process.pfPileUp.checkClosestZVertex = False

  #-------------------------------------------------
  # selection step 2: vertex filter
  #-------------------------------------------------

  # https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookJetEnergyCorrections#JetEnCorPFnoPU2012
  # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefEventSel#Cleaning_Filters
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

  process.pfIsolatedMuons.isolationCut = maxLeptonIso

  # muon ID production (essentially track count embedding) must be here
  # because tracks get dropped from the collection after this step, resulting
  # in null ptrs.
  process.muonsWithID = cms.EDProducer(
    'MuonIDProducer',
    muonSrc = cms.InputTag("selectedPatMuons"),
    primaryVertexSource = cms.InputTag("goodOfflinePrimaryVertices")
  )

  #-------------------------------------------------
  # Electrons
  # Implemented as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=208765
  #-------------------------------------------------

  process.load('EGamma.EGammaAnalysisTools.electronIdMVAProducer_cfi')
  process.mvaID = cms.Sequence(process.mvaTrigV0 + process.mvaNonTrigV0)
  process.patElectrons.electronIDSources.mvaTrigV0 = cms.InputTag("mvaTrigV0")
  process.patElectrons.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0")
  process.patPF2PATSequence.replace(process.patElectrons, process.mvaID * process.patElectrons)
  process.electronsWithID = cms.EDProducer(
    'ElectronIDProducer',
    electronSrc = cms.InputTag("selectedPatElectrons"),
    primaryVertexSource = cms.InputTag("goodOfflinePrimaryVertices")
  )
  process.pfIsolatedElectrons.isolationCut = maxLeptonIso
  #electron dR=0.3
  process.pfElectrons.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFId"))
  process.pfElectrons.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFId")
  process.pfElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))
  
  process.pfIsolatedElectrons.isolationValueMapsCharged = cms.VInputTag(cms.InputTag("elPFIsoValueCharged03PFId"))
  process.pfIsolatedElectrons.deltaBetaIsolationValueMap = cms.InputTag("elPFIsoValuePU03PFId")
  process.pfIsolatedElectrons.isolationValueMapsNeutral = cms.VInputTag(cms.InputTag("elPFIsoValueNeutral03PFId"), cms.InputTag("elPFIsoValueGamma03PFId"))


  #-------------------------------------------------
  # Jets
  # MET corrections as https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookMetAnalysis#Type_I_0_with_PAT
  #-------------------------------------------------

  #pfNoTau == True => remove taus from jets
  #process.pfNoTau.enable = noTau

  #process.selectedPatJets.cut = cms.string("pt>30")
  process.load("CMGTools.External.pujetidsequence_cff")
  process.patPF2PATSequence.insert(-1, process.puJetIdSqeuence)

  #-------------------------------------------------
  # Paths
  #-------------------------------------------------

  #process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatElectrons) + 1, process.elesWithIso)
  process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatMuons) + 1, process.muonsWithID)
  process.patPF2PATSequence.insert(process.patPF2PATSequence.index(process.selectedPatElectrons) + 1, process.electronsWithID)

  #Need separate paths because of skimming

  if doMuon:
    process.singleTopPathStep1Mu = cms.Path(
      process.goodOfflinePrimaryVertices
      * process.patPF2PATSequence
    )

  if doElectron:
    process.singleTopPathStep1Ele = cms.Path(
      process.goodOfflinePrimaryVertices
      * process.patPF2PATSequence
    )

  #-----------------------------------------------
  # Skimming
  #-----------------------------------------------

  #Throw away events before particle flow?
  if doSkimming:
      from SingleTopPolarization.Analysis.eventSkimming import skimFilters
      skimFilters(process)

      if doMuon:
        process.singleTopPathStep1Mu.insert(0, process.muonSkim)
      if doElectron:
        process.singleTopPathStep1Ele.insert(0, process.electronSkim)

  #-----------------------------------------------
  # Skim efficiency counters
  #-----------------------------------------------

  #count all processed events
  countProcessed(process)

  #count events passing mu and ele paths

  if doMuon:
    countInSequence(process, process.singleTopPathStep1Mu)
  if doElectron:
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

          # Jets
          'keep patJets_selectedPatJets__PAT',
          'keep double_*_rho_RECO', #For rho-corr rel iso
          'keep recoGenJets_selectedPatJets_genJets_PAT', #For Jet MC smearing we need to keep the genJets
          "keep *_puJetId_*_*", # input variables
          "keep *_puJetMva_*_*", # final MVAs and working point flags

          # Muons
          'keep patMuons_muonsWithID__PAT',

          # Electrons
          'keep patElectrons_electronsWithID__PAT',

          # METs
          'keep patMETs_patMETs__PAT',

          #ECAL laser corr filter
          'keep bool_ecalLaserCorrFilter__PAT'
      ])

  #Keep events that pass either the muon OR the electron path
  process.out.SelectEvents = cms.untracked.PSet(
    SelectEvents = cms.vstring(
      []
    )
  )
  if doMuon:
    process.out.SelectEvents.SelectEvents.append("singleTopPathStep1Mu")
  if doElectron:
    process.out.SelectEvents.SelectEvents.append("singleTopPathStep1Ele")

  if isMC:
    process.GlobalTag.globaltag = cms.string('START53_V7F::All')
  else:
    process.GlobalTag.globaltag = cms.string(globalTag) #FT_53_V6_AN2
    process.load('RecoMET.METFilters.ecalLaserCorrFilter_cfi')
    process.ecalLaserCorrFilter.taggingMode=True

    # https://twiki.cern.ch/twiki/bin/viewauth/CMS/TWikiTopRefEventSel#Cleaning_Filters
    process.scrapingFilter = cms.EDFilter("FilterOutScraping"
      , applyfilter = cms.untracked.bool(True)
      , debugOn = cms.untracked.bool(False)
      , numtrack = cms.untracked.uint32(10)
      , thresh = cms.untracked.double(0.25)
    )

    if doElectron:
      process.singleTopPathStep1Ele.insert(0, process.scrapingFilter)
    if doMuon:
      process.singleTopPathStep1Mu.insert(0, process.scrapingFilter)

    process.patPF2PATSequence.insert(-1, process.ecalLaserCorrFilter)

  if not onGrid:
    from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
    enableCommandLineArguments(process)
  else:
    process.out.fileName = "step1.root"

  if doSkimming:
    process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_Skim.root"))
  else:
    process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_noSkim.root"))
  print 80*"-"
  print "Output file is %s" % process.out.fileName
  print "isMC: %s" % str(isMC)
  print "ele path: " + str(process.singleTopPathStep1Ele)
  print "mu path: " + str(process.singleTopPathStep1Mu)
  print "outputCommands: " + str(process.out.outputCommands) 

  if not doSlimming:
    process.out.fileName.setValue(process.out.fileName.value().replace(".root", "_noSlim.root"))
