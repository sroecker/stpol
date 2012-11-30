import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

def SingleTopStep2(isMC,
    skipPatTupleOutput=True,
    onGrid=False,
    filterHLT=False,
    doDebug=False,
    doMuon=True,
    doElectron=True,
    channel="sig",
    nJets=2, nBTags=1,
    reverseIsoCut=False,
    muonIsoType="deltaBetaCorrRelIso",
    eleMetType="MtW",
    cutJets=True,
    eleMVACut=0.1,
    electronPt="ecalDrivenMomentum.Pt()"
    ):
    
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
        process.MessageLogger.cerr.threshold = cms.untracked.string("ERROR")

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
    JetSetup(process, isMC, doDebug, nJets=nJets, nBTags=nBTags, cutJets=cutJets)

    #-------------------------------------------------
    # Leptons
    #-------------------------------------------------

    process.muonsWithIso = cms.EDProducer(
      'MuonIsolationProducer',
      leptonSrc = cms.InputTag("muonsWithID"),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.4)
    )

    process.elesWithIso = cms.EDProducer(
      'ElectronIsolationProducer',
      leptonSrc = cms.InputTag("electronsWithID"),
      rhoSrc = cms.InputTag("kt6PFJets", "rho"),
      dR = cms.double(0.3)
    )

    from SingleTopPolarization.Analysis.muons_step2_cfi import MuonSetup
    MuonSetup(process, isMC, doDebug=doDebug, reverseIsoCut=reverseIsoCut, isoType=muonIsoType)

    from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronSetup
    ElectronSetup(process, isMC, doDebug=doDebug, reverseIsoCut=reverseIsoCut, metType=eleMetType, mvaCut=eleMVACut, electronPt=electronPt)

    process.goodSignalLeptons = cms.EDProducer(
         'CandRefCombiner',
         sources=cms.untracked.vstring(["goodSignalMuons", "goodSignalElectrons"]),
             maxOut=cms.untracked.uint32(1),
             minOut=cms.untracked.uint32(1)
    )

    #-----------------------------------------------
    # Top reco and cosine calcs
    #-----------------------------------------------

    from SingleTopPolarization.Analysis.top_step2_cfi import TopRecoSetup
    TopRecoSetup(process, untaggedSource="fwdMostLightJet")

    #-----------------------------------------------
    # Treemaking
    #-----------------------------------------------


    def treeCollection(collection_, maxElems_, varlist):
        varVPSet = cms.untracked.VPSet()
        for v in varlist:
            pset = cms.untracked.PSet(tag=cms.untracked.string(v[0]), expr=cms.untracked.string(v[1]), )
            varVPSet.append(pset)
        ret = cms.untracked.PSet(
            collection=collection_,
            maxElems=cms.untracked.int32(maxElems_),
            variables=varVPSet
        )
        return ret

    process.treesMu = cms.EDAnalyzer('MuonCandViewTreemakerAnalyzer',
            collections = cms.untracked.VPSet(
            treeCollection(
                cms.untracked.InputTag("goodSignalMuons"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["relIso", "userFloat('%s')" % muonIsoType],
                    ["Charge", "charge"],
                ]
                )
            )
    )

    process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
            collections = cms.untracked.VPSet(
            treeCollection(
                cms.untracked.InputTag("goodSignalElectrons"), 1,
                [
                    ["Pt", "%s" % electronPt],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["relIso", "userFloat('rhoCorrRelIso')"],
                    ["mvaID", "electronID('mvaTrigV0')"],
                    ["Charge", "charge"],
                ]
                )
            )
    )
    process.treesJets = cms.EDAnalyzer('JetCandViewTreemakerAnalyzer',
            collections = cms.untracked.VPSet(
            treeCollection(
                cms.untracked.InputTag("untaggedJets"), nJets-nBTags,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                    ["bDiscriminator", "bDiscriminator('combinedSecondaryVertexBJetTags')"],
                    ["rms", "userFloat('rms')"]
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("fwdMostLightJet"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                    ["bDiscriminator", "bDiscriminator('combinedSecondaryVertexBJetTags')"],
                    ["rms", "userFloat('rms')"]
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("highestBTagJet"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                    ["bDiscriminator", "bDiscriminator('combinedSecondaryVertexBJetTags')"],
                    ["rms", "userFloat('rms')"]
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("btaggedJets"), nBTags,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                    ["bDiscriminator", "bDiscriminator('combinedSecondaryVertexBJetTags')"],
                    ["rms", "userFloat('rms')"]
                ]
            )
        )
    )



    #process.treesEle = cms.EDAnalyzer('ElectronCandViewTreemakerAnalyzer',
    #        collections = cms.untracked.VPSet(treeCollection("goodSignalElectrons", 1,
    #            [
    #                ["Pt", "pt"],
    #                ["Eta", "eta"],
    #                ["Phi", "phi"],
    #                ["rhoCorrRelIso", "userFloat('rhoCorrRelIso')"],
    #            ]
    #            )
    #        )
    #)

    process.treesCands = cms.EDAnalyzer('CandViewTreemakerAnalyzer',
            collections = cms.untracked.VPSet(
            treeCollection(
                cms.untracked.InputTag("recoTop"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("recoNu"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Px", "p4().Px()"],
                    ["Py", "p4().Py()"],
                    ["Pz", "p4().Pz()"],
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("genParticleSelector", "trueTop", "STPOLSEL2"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Mass", "mass"],
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("genParticleSelector", "trueNeutrino", "STPOLSEL2"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                    ["Px", "p4().Px()"],
                    ["Py", "p4().Py()"],
                    ["Pz", "p4().Pz()"],
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("genParticleSelector", "trueLepton", "STPOLSEL2"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                ]
            ),
            treeCollection(
                cms.untracked.InputTag("genParticleSelector", "trueLightJet", "STPOLSEL2"), 1,
                [
                    ["Pt", "pt"],
                    ["Eta", "eta"],
                    ["Phi", "phi"],
                ]
            ),
        )
    )

    process.treesDouble = cms.EDAnalyzer("DoubleTreemakerAnalyzer",
        collections = cms.VInputTag(
            #Merged cosTheta*
            cms.InputTag("cosTheta", "cosThetaLightJet"),

            #cosTheta* separately from mu and ele
            #cms.InputTag("cosThetaProducerEle", "cosThetaLightJet"),
            #cms.InputTag("cosThetaProducerMu", "cosThetaLightJet"),

            #cosTheta* from gen
            cms.InputTag("cosThetaProducerTrueTop", "cosThetaLightJet"),
            cms.InputTag("cosThetaProducerTrueLepton", "cosThetaLightJet"),
            cms.InputTag("cosThetaProducerTrueJet", "cosThetaLightJet"),
            cms.InputTag("cosThetaProducerTrueAll", "cosThetaLightJet"),


            #Transverse mass of MET and lepton
            cms.InputTag("muAndMETMT", ""),
            cms.InputTag("eleAndMETMT", ""),

            #Some debugging data
            cms.InputTag("kt6PFJets", "rho", "RECO"),
            cms.InputTag("recoNu", "Delta"),
        )
    )

    process.treesBool = cms.EDAnalyzer("BoolTreemakerAnalyzer",
        collections = cms.VInputTag(
            cms.InputTag("ecalLaserCorrFilter", "", "PAT"),
        )
    )

    process.treesInt = cms.EDAnalyzer("IntTreemakerAnalyzer",
        collections = cms.VInputTag(
            [
            cms.InputTag("recoNuProducerMu", "solType"),
            cms.InputTag("recoNuProducerEle ", "solType"),
            cms.InputTag("muonCount"),
            cms.InputTag("electronCount"),
            cms.InputTag("topCount"),
            cms.InputTag("bJetCount"),
            cms.InputTag("lightJetCount")
            ]
        )
    )

    process.treeSequence = cms.Sequence(process.treesMu*process.treesEle*process.treesDouble*process.treesBool*process.treesCands*process.treesJets*process.treesInt)

    #-----------------------------------------------
    # Paths
    #-----------------------------------------------

    from SingleTopPolarization.Analysis.hlt_step2_cfi import HLTSetup
    HLTSetup(process, isMC, filterHLT)

    if isMC and channel=="sig":
        from SingleTopPolarization.Analysis.partonStudy_step2_cfi import PartonStudySetup
        PartonStudySetup(process)
        process.partonPath = cms.Path(process.partonStudyTrueSequence)

    if doDebug:
        from SingleTopPolarization.Analysis.debugAnalyzers_step2_cfi import DebugAnalyzerSetup
        DebugAnalyzerSetup(process)

    if doMuon:
        from SingleTopPolarization.Analysis.muons_step2_cfi import MuonPath
        MuonPath(process, isMC, channel)
        process.muPath.insert(process.muPath.index(process.oneIsoMu)+1, process.goodSignalLeptons)

    if doElectron:
        from SingleTopPolarization.Analysis.electrons_step2_cfi import ElectronPath
        ElectronPath(process, isMC, channel, doDebug=doDebug)
        process.elePath.insert(process.elePath.index(process.oneIsoEle)+1, process.goodSignalLeptons)

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
                #'drop patElectrons_looseVetoElectrons__PAT',
                #'drop patMuons_looseVetoMuons__PAT',
                #'drop *_recoNuProducerEle_*_*',
                #'drop *_recoNuProducerMu_*_*',
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
    print "isMC: %s" % str(isMC)

    print "onGrid: %s" % str(onGrid)
    print "channel: %s" % channel

    print "lepton antiIso: %s" % reverseIsoCut

    print ""
    print "Running paths: %s" % str(process.paths.list)
    for p in process.paths.list:
        print "%s -> %s" % (p, process.paths.get(p))
    print ""

    print "Output trees: %s" % process.TFileService.fileName.value()
    if hasattr(process, "out"):
        print "Output patTuples: %s" % process.out.fileName.value()
    print 80*"-"
    print "Step2 configured"

    return process
