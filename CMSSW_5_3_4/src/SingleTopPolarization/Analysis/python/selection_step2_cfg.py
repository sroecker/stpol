import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

def SingleTopStep2(isMC, skipPatTupleOutput=True, onGrid=False, filterHLT=False, doDebug=False, doMuon=True, doElectron=True):
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

    from SingleTopPolarization.Analysis.jets_step2_cfi import JetSetup
    JetSetup(process, isMC)

    #-------------------------------------------------
    # Muons
    #-------------------------------------------------

    if doMuon:
        from SingleTopPolarization.Analysis.muons_step2_cfi import MuonSetup
        MuonSetup(process, isMC)

    #-------------------------------------------------
    # Electrons
    #-------------------------------------------------

    if doElectron:
        from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronSetup
        ElectronSetup(process, isMC)

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
            cms.InputTag("cosThetaProducerTrueTopMu", "cosThetaLightJet", "STPOLSEL2"),
            cms.InputTag("trueCosThetaProducerMu", "cosThetaLightJet", "STPOLSEL2"),
            cms.InputTag("muAndMETMT", "", "STPOLSEL2"),
            cms.InputTag("kt6PFJets", "rho", "RECO"),
            cms.InputTag("recoNuProducerMu", "Delta", "STPOLSEL2"),
            cms.InputTag("recoNuProducerEle", "Delta", "STPOLSEL2")
        )
    )

    process.treesBool = cms.EDAnalyzer("BoolTreemakerAnalyzer",
        collections = cms.VInputTag(
            cms.InputTag("ecalLaserCorrFilter", "", "PAT"),
        )
    )

    process.treeSequence = cms.Sequence(process.treesMu*process.treesEle*process.treesDouble*process.treesBool)

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

    from SingleTopPolarization.Analysis.hlt_step2_cfi import HLTSetup
    HLTSetup(process, isMC, filterHLT)

    # #Combine reconstuctd muon and electron collections to a single reconstructed lepton collection
    # process.goodSignalLeptons = cms.EDProducer(
    #     'CandRefCombiner',
    #     sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
    #     minOut=cms.untracked.uint32(1),
    #     maxOut=cms.untracked.uint32(1),
    # )

    # #Combine muon-derived and electron-derived neutrino collections to a single recoNu colletion
    # process.recoNu = cms.EDProducer(
    #     #'CompositeCandCollectionCombiner',
    #     'CandRefCombiner',
    #     sources=cms.untracked.vstring(["recoNuProducerEle", "recoNuProducerMu"]),
    #     minOut=cms.untracked.uint32(1),
    #     maxOut=cms.untracked.uint32(1),
    # )

    if isMC:
        process.cosThetaProducerTrueTopMu = cms.EDProducer('CosThetaProducer',
            topSrc=cms.InputTag("genParticleSelectorMu", "trueTop"),
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
            src = cms.InputTag("untaggedJets"),
            trueSrc = cms.InputTag("genParticleSelectorMu", "trueLightJet"),
            maxMass=cms.untracked.double(40.)
        )

        process.topComparer = cms.EDAnalyzer('ParticleComparer',
            src = cms.InputTag("recoTopMu"),
            trueSrc = cms.InputTag("genParticleSelectorMu", "trueTop"),
            maxMass=cms.untracked.double(300.)
        )

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
        from SingleTopPolarization.Analysis.muons_step2_cfi import MuonPath
        MuonPath(process, isMC)

    if doElectron:
        from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronPath
        ElectronPath(process, isMC)

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
