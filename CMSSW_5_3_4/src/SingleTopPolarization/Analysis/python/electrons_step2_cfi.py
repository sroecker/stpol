import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

def ElectronSetup(process, isMC, mvaCut=0.1, doDebug=False):


	goodElectronCut = "pt>30"
	goodElectronCut += "&& abs(eta)<2.5"
	goodElectronCut += "&& !(1.4442 < abs(superCluster.eta) < 1.5660)"
	goodElectronCut += "&& passConversionVeto()"
	#goodElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
	goodElectronCut += "&& electronID('mvaTrigV0') > %f" % mvaCut

	goodSignalElectronCut = goodElectronCut
	goodSignalElectronCut += '&& userFloat("rhoCorrRelIso") < 0.1'
	goodSignalElectronCut += '&& abs(userFloat("dxy")) < 0.02'
	goodSignalElectronCut += '&& userInt("gsfTrack_trackerExpectedHitsInner_numberOfHits") <= 0'

	goodQCDElectronCut = goodElectronCut
	goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") > 0.2'
	goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") < 0.5'

	looseVetoElectronCut = "pt > 20"
	looseVetoElectronCut += "&& abs(eta) < 2.5"
	#looseVetoElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
	looseVetoElectronCut += "&& electronID('mvaTrigV0') > %f" % mvaCut
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

	process.electronCount = cms.EDProducer(
		"CollectionSizeProducer<reco::Candidate>",
		src = cms.InputTag("goodSignalElectrons")
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

	process.recoNuProducerEle = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
		leptonSrc=cms.InputTag("goodSignalLeptons"),
		bjetSrc=cms.InputTag("btaggedJets"),
		metSrc=cms.InputTag("patMETs"), #either patMETs if cutting on ele + MET transverse mass or goodMETs if cutting on patMETs->goodMets pt
	)

	if doDebug:
		process.oneIsoEleIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("oneIsoEle"))
		process.metIDS = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("MET"))
		process.electronAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("elesWithIso"))

def ElectronPath(process, isMC, channel, doDebug=False):
	process.elePathPreCount = cms.EDProducer("EventCountProducer")

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

	process.elePath = cms.Path(

		process.muonsWithIso *
		process.elesWithIso *

		process.elePathPreCount *

		process.stepHLTsyncEle *

		process.goodSignalElectrons *
		process.electronCount *
		process.goodQCDElectrons *
		process.looseVetoElectrons *
		process.oneIsoEle *

		#process.oneIsoEleIDs *

		process.looseEleVetoEle *
		process.looseVetoMuons *
		process.looseMuVetoEle *

		process.jetSequence *
		process.nJets *

		#process.goodMETs *
		process.eleAndMETMT *
		process.hasEleMETMT *

		process.goodSignalLeptons *

		process.mBTags *

		process.topRecoSequenceEle *

		process.efficiencyAnalyzerEle
	)

	if doDebug:
		process.elePath.insert(
			process.elePath.index(process.oneIsoEle)+1,
			process.oneIsoEleIDs
		)
		process.elePath.insert(
			process.elePath.index(process.oneIsoEle),
			process.electronAnalyzer
		)
		process.elePath.insert(
			process.elePath.index(process.hasEleMETMT)+1,
			process.metIDS
		)


	if isMC and channel=="sig":
		process.elePath.insert(
			process.elePath.index(process.topRecoSequenceEle)+1,
			process.partonStudyCompareSequence
		)

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
