import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

def SingleTopStep2(isMC, skipPatTupleOutput=True, onGrid=False, filterHLT=False, doDebug=False, doMuon=True, doElectron=True, bTag="combinedSecondaryVertexBJetTags", bTagCut=0.679):
    process = cms.Process("STPOLSEL2")
    eventCounting.countProcessed(process)

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
        process.MessageLogger.cerr.FwkReport.reportEvery = 1000

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

    if isMC:
        jetCut = 'userFloat("pt_smear") > 40.'
    else:
        jetCut = 'pt > 40'

    jetCut += ' && abs(eta) < 4.7'                                        # pseudo-rapidity range
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

    if isMC:
        process.smearedJets = cms.EDProducer('JetMCSmearProducer',
            src=cms.InputTag("noPUJets"),
            reportMissingGenJet=cms.untracked.bool(doDebug)
        )

    process.goodJets = cms.EDFilter("CandViewSelector",
        src=cms.InputTag("smearedJets" if isMC else 'noPUJets'),
        cut=cms.string(jetCut)
    )

    bTagCutStr = 'bDiscriminator("%s") >= %f' % (bTag, bTagCut)

    process.btaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr)
    )

    process.untaggedJets = cms.EDFilter(
        "CandViewSelector",
        src=cms.InputTag("goodJets"),
        cut=cms.string(bTagCutStr.replace(">=", "<"))
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
        src=cms.InputTag("btaggedJets"),
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
        bjetSrc=cms.InputTag("btaggedJets"),
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
      leptonSrc = cms.InputTag("electronsWithID"),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.4)
    )

    goodElectronCut = "pt>30"
    goodElectronCut += "&& abs(eta)<2.5"
    goodElectronCut += "&& !(1.4442 < abs(superCluster.eta) < 1.5660)"
    goodElectronCut += "&& passConversionVeto()"
    #goodElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
    goodElectronCut += "&& electronID('mvaTrigV0') > 0.1"

    goodSignalElectronCut = goodElectronCut
    goodSignalElectronCut += '&& userFloat("rhoCorrRelIso") < 0.1'
    goodSignalElectronCut += '&& abs(userFloat("dxy")) < 0.2'
    goodSignalElectronCut += '&& userInt("gsfTrack_trackerExpectedHitsInner_numberOfHits") <= 0'

    goodQCDElectronCut = goodElectronCut
    goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") > 0.2'
    goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") < 0.5'

    looseVetoElectronCut = "pt > 20"
    looseVetoElectronCut += "&& abs(eta) < 2.5"
    #looseVetoElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
    looseVetoElectronCut += "&& electronID('mvaTrigV0') > 0.1"
    looseVetoElectronCut += '&& userFloat("rhoCorrRelIso") < 0.3'

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

    process.eleAndMETMT = cms.EDProducer('CandTransverseMassProducer',
        collections=cms.untracked.vstring(["patMETs", "goodSignalElectrons"])
    )

    process.hasEleMETMT = cms.EDFilter('EventDoubleFilter',
        src=cms.InputTag("eleAndMETMT"),
        min=cms.double(35),
        max=cms.double(9999999)
    )

    process.recoNuProducerEle = cms.EDProducer('ReconstructedNeutrinoProducer',
        leptonSrc=cms.InputTag("goodSignalLeptons"),
        bjetSrc=cms.InputTag("btaggedJets"),
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
            cms.InputTag("trueCosThetaProducerMu", "cosThetaLightJet", "STPOLSEL2"),
            cms.InputTag("muAndMETMT", "", "STPOLSEL2"),
            cms.InputTag("kt6PFJets", "rho", "RECO"),
            cms.InputTag("recoNuProducerMu", "Delta", "STPOLSEL2"),
            cms.InputTag("recoNuProducerEle", "Delta", "STPOLSEL2")
        )
    )

    process.treesDouble

    process.treesBool = cms.EDAnalyzer("BoolTreemakerAnalyzer",
        collections = cms.VInputTag(
            cms.InputTag("ecalLaserCorrFilter", "", "PAT"),
        )
    )
    process.treeSequence = cms.Sequence(process.treesMu*process.treesEle*process.treesDouble)
    if not isMC:
        process.treeSequence.insert(-1, process.treesBool)

    if doMuon:
        process.efficiencyAnalyzerMu = cms.EDAnalyzer('EfficiencyAnalyzer'
        , histogrammableCounters = cms.untracked.vstring(["muPath"])
        , muPath = cms.untracked.vstring([
            "singleTopPathStep1MuPreCount",
            "singleTopPathStep1MuPostCount",
            "muPathPreCount",
            "muPathStepHLTsyncMuPostCount",
            "muPathOneIsoMuPostCount",
            "muPathLooseMuVetoMuPostCount",
            "muPathLooseEleVetoMuPostCount",
            "muPathNJetsPostCount",
            "muPathHasMuMETMTPostCount",
            "muPathMBTagsPostCount"
            ]
        ))

    if doElectron:
        process.efficiencyAnalyzerEle = cms.EDAnalyzer('EfficiencyAnalyzer'
        , histogrammableCounters = cms.untracked.vstring(["elePath"])
        , elePath = cms.untracked.vstring([
            "singleTopPathStep1ElePreCount",
            "singleTopPathStep1ElePostCount",
            "elePathPreCount",
            "elePathStepHLTsyncElePostCount",
            "elePathOneIsoElePostCount",
            "elePathLooseEleVetoElePostCount",
            "elePathLooseMuVetoElePostCount",
            "elePathNJetsPostCount",
            "elePathHasEleMETMTPostCount",
            "elePathMBTagsPostCount"
            ]
        ))

    #-----------------------------------------------
    # Paths
    #-----------------------------------------------


    #HLTT
    import HLTrigger.HLTfilters.triggerResultsFilter_cfi as HLT

    process.stepHLTsyncMu = HLT.triggerResultsFilter.clone(
            hltResults = cms.InputTag( "TriggerResults","","HLT"),
            l1tResults = '',
            throw = False
            )

    process.stepHLTsyncEle = HLT.triggerResultsFilter.clone(
            hltResults = cms.InputTag( "TriggerResults","","HLT"),
            l1tResults = '',
            throw = False
            )

    if filterHLT:
        process.stepHLTsyncMu.triggerConditions = ["HLT_IsoMu24_eta2p1_v* OR HLT_IsoMu17_eta2p1_CentralPFNoPUJet30_BTagIPIter_v*"]
        process.stepHLTsyncEle.triggerConditions = ["HLT_Ele27_WP80_v* OR HLT_Ele25_CaloIdVT_CaloIsoT_TrkIdT_TrkIsoT_CentralPFNoPUJet30_BTagIPIter_v*"]
    else:
        process.stepHLTsyncMu.triggerConditions = ["HLT_*"]
        process.stepHLTsyncEle.triggerConditions = ["HLT_*"]

    #Combine reconstuctd muon and electron collections to a single reconstructed lepton collection
    process.goodSignalLeptons = cms.EDProducer(
        'CandRefCombiner',
        sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
        minOut=cms.untracked.uint32(1),
        maxOut=cms.untracked.uint32(1),
    )

    #Combine muon-derived and electron-derived neutrino collections to a single recoNu colletion
    process.recoNu = cms.EDProducer(
        #'CompositeCandCollectionCombiner',
        'CandRefCombiner',
        sources=cms.untracked.vstring(["recoNuProducerEle", "recoNuProducerMu"]),
        minOut=cms.untracked.uint32(1),
        maxOut=cms.untracked.uint32(1),
    )

    #Reconstruct the 4-momentum of the top quark by adding the momenta of the b-jet, the neutrino and the charged lepton
    process.recoTopEle = cms.EDProducer('SimpleCompositeCandProducer',
        sources=cms.VInputTag(["recoNuProducerEle", "btaggedJets", "goodSignalElectrons"])
    )

    process.recoTopMu = cms.EDProducer('SimpleCompositeCandProducer',
        sources=cms.VInputTag(["recoNuProducerMu", "btaggedJets", "goodSignalMuons"])
    )


    #Calculate the cosTheta* between the untagged jet and the lepton in the top CM frame
    process.cosThetaProducerEle = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTopEle"),
        jetSrc=cms.InputTag("untaggedJets"),
        leptonSrc=cms.InputTag("goodSignalElectrons")
    )

    process.cosThetaProducerMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("recoTopMu"),
        jetSrc=cms.InputTag("untaggedJets"),
        leptonSrc=cms.InputTag("goodSignalMuons")
    )

    #Select the generated top quark, light jet and charged lepton
    process.genParticleSelectorMu = cms.EDProducer('GenParticleSelector',
	     src=cms.InputTag("genParticles")
    )

    process.hasMuon = cms.EDFilter(
        "PATCandViewCountFilter",
        src=cms.InputTag("genParticleSelectorMu", "trueLepton"),
        minNumber=cms.uint32(1),
        maxNumber=cms.uint32(1),
    )

    process.trueCosThetaProducerMu = cms.EDProducer('CosThetaProducer',
        topSrc=cms.InputTag("genParticleSelectorMu", "trueTop"),
        jetSrc=cms.InputTag("genParticleSelectorMu", "trueLightJet"),
        leptonSrc=cms.InputTag("genParticleSelectorMu", "trueLepton")
    )

    process.matrixCreator = cms.EDAnalyzer('TransferMatrixCreator',
        src = cms.InputTag("cosThetaProducerMu", "cosThetaLightJet"),
        trueSrc = cms.InputTag("trueCosThetaProducerMu", "cosThetaLightJet")
    )

    process.leptonComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("goodSignalLeptons"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueLepton"),
        maxMass=cms.untracked.double(.3)
    )

    process.jetComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("untaggedTCHPtight"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueLightJet"),
        maxMass=cms.untracked.double(40.)
    )

    process.topComparer = cms.EDAnalyzer('ParticleComparer',
        src = cms.InputTag("recoTopMu"),
        trueSrc = cms.InputTag("genParticleSelectorMu", "trueTop"),
        maxMass=cms.untracked.double(300.)
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


    if doDebug:
        process.oneIsoMuIDs = cms.EDAnalyzer('EventIDAnalyzer',
            name=cms.untracked.string("oneIsoMu")
        )

        process.nJetIDs = cms.EDAnalyzer('EventIDAnalyzer',
            name=cms.untracked.string("nJetIDs")
        )

        process.goodMuonsAnalyzer = cms.EDAnalyzer(
            'SimpleMuonAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["goodSignalMuons"])
        )

        process.selectedPatElectronsAnalyzer = cms.EDAnalyzer(
            'SimpleElectronAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["electronsWithID"])
        )

        process.goodElectronsAnalyzer = cms.EDAnalyzer(
            'SimpleElectronAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["goodSignalElectrons"])
        )

        process.selectedPatMuonsAnalyzer = cms.EDAnalyzer(
            'SimpleMuonAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["muonsWithID"])
        )

        process.eleAnalyzer = cms.EDAnalyzer(
            'SimpleEventAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["selectedPatElectrons"])
        )

        process.patJetsAnalyzer = cms.EDAnalyzer(
            'SimpleJetAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["selectedPatJets"])
        )

        process.goodJetsPreAnalyzer = cms.EDAnalyzer(
            'SimpleJetAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["smearedJets"])
        )
        process.goodJetsPostAnalyzer = cms.EDAnalyzer(
            'SimpleJetAnalyzer',
            interestingCollections = cms.untracked.VInputTag(["goodJets"])
        )

        process.dumpContent = cms.EDAnalyzer('EventContentAnalyzer')

    if doMuon:
        process.muPathPreCount = cms.EDProducer("EventCountProducer")
        process.muPath = cms.Path(
            process.muonsWithIso *
            process.elesWithIso *

            process.muPathPreCount *

            #Optionally select the HLT
            process.stepHLTsyncMu *

            #Select one isolated muon and veto additional loose muon/electron
            process.goodSignalMuons *
            process.goodQCDMuons *
            process.looseVetoMuons *
            process.oneIsoMu *
            process.looseMuVetoMu *
            process.looseVetoElectrons *
            process.looseEleVetoMu *

            #Do PU-jet cleaning, and select 2 good jets
            process.noPUJets *
            process.goodJets *
            process.nJets *

            #Select mu and MET invariant transverse mass
            process.muAndMETMT *
            process.hasMuMETMT *

            #Reconstruct the neutrino
            process.goodSignalLeptons *
            process.recoNuProducerMu *
            process.recoNu *

            #Select b-tagged jets and events with ==1 btag
            process.btaggedJets *
            process.untaggedJets *
            process.mBTags *

            #Reconstruct the top quark and calculate the cosTheta* variable
            process.recoTopMu *
            process.cosThetaProducerMu *
            process.efficiencyAnalyzerMu
        )
        if isMC:
            #in MC we need to smear the reconstucted jet pt, E
            process.muPath.insert(process.muPath.index(process.noPUJets)+1, process.smearedJets)

            process.muPath.insert(0, process.genParticleSelectorMu * process.hasMuon * process.trueCosThetaProducerMu)
            process.muPath.insert(process.muPath.index(process.cosThetaProducerMu)+1,
            process.matrixCreator * process.leptonComparer * process.jetComparer * process.topComparer)

        #Count number of events passing the selection filters
        eventCounting.countAfter(process, process.muPath,
            [
            "stepHLTsyncMu",
            "oneIsoMu",
            "looseMuVetoMu",
            "looseEleVetoMu",
            "hasMuMETMT",
            "nJets",
            "mBTags"
            ]
        )

    if doElectron:
        process.elePathPreCount = cms.EDProducer("EventCountProducer")
        process.elePath = cms.Path(

            process.muonsWithIso *
            process.elesWithIso *

            process.elePathPreCount *

            process.stepHLTsyncEle *

            process.goodSignalElectrons *
            process.goodQCDElectrons *
            process.looseVetoElectrons *
            process.selectedPatElectronsAnalyzer *
            process.oneIsoEle *
            process.goodElectronsAnalyzer *
            process.looseEleVetoEle *
            process.looseVetoMuons *
            process.looseMuVetoEle *

            process.noPUJets *
            process.goodJets *
            process.nJets *

            process.goodMETs *
            process.eleAndMETMT *
            process.hasEleMETMT *

            process.goodSignalLeptons *
            process.recoNuProducerEle *
            process.recoNu *

            process.btaggedJets *
            process.untaggedJets *
            process.mBTags *

            process.recoTopEle *
            process.cosThetaProducerEle *
            process.efficiencyAnalyzerEle
        )
        if isMC:
            process.elePath.insert(process.elePath.index(process.noPUJets)+1, process.smearedJets)

        eventCounting.countAfter(process, process.elePath,
            [
            "stepHLTsyncEle",
            "oneIsoEle",
            "looseEleVetoEle",
            "looseMuVetoEle",
            "hasEleMETMT",
            "nJets",
            "mBTags"
            ]
        )

    process.treePath = cms.Path(process.treeSequence)


    #-----------------------------------------------
    # Outpath
    #-----------------------------------------------
    if not skipPatTupleOutput:
        process.out = cms.OutputModule("PoolOutputModule",
            fileName=cms.untracked.string('out_step2.root'),
             SelectEvents=cms.untracked.PSet(
                 SelectEvents=cms.vstring([])
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
        if doElectron:
            process.out.SelectEvents.SelectEvents.append("elePath")
        if doMuon:
            process.out.SelectEvents.SelectEvents.append("muPath")

    #-----------------------------------------------
    #
    #-----------------------------------------------

    #Command-line arguments
    if not onGrid:
        from SingleTopPolarization.Analysis.cmdlineParsing import enableCommandLineArguments
        (inFiles, outFile) = enableCommandLineArguments(process)
    else:
        outFile = "step2.root"

    process.TFileService = cms.Service(
        "TFileService",
        fileName=cms.string(outFile.replace(".root", "_trees.root")),
    )
    print "Step2 configured"
    return process
