import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

"""
This method sets up the electron channel lepton selection.
isMC - run on MC (vs. run on data)
mvaCut - the electron multivariate ID cut (electrons with MVA<cut pass as signal electrons)
doDebug - enable various debugging printout modules
metType - choose either between 'MtW' for the W transverse mass or 'MET' for a simple MET cut
reverseIsoCut - 'True' to choose the anti-isolated leptons, 'False' to choose isolated leptons
"""
def ElectronSetup(
	process,
	isMC,
	mvaCut=0.1,
	doDebug=False,
	metType="MtW",
	reverseIsoCut=False,
	applyMVA=True,
	electronPt="ecalDrivenMomentum.Pt()"
	):


	goodElectronCut = "%s>30" % electronPt
	goodElectronCut += "&& abs(eta)<2.5"
	goodElectronCut += "&& !(1.4442 < abs(superCluster.eta) < 1.5660)"
	goodElectronCut += "&& passConversionVeto()"
	#goodElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
	if applyMVA:
		goodElectronCut += "&& electronID('mvaTrigV0') > %f" % mvaCut

	goodSignalElectronCut = goodElectronCut
	goodSignalElectronCut += '&& abs(userFloat("dxy")) < 0.02'
	goodSignalElectronCut += '&& userInt("gsfTrack_trackerExpectedHitsInner_numberOfHits") <= 0'

	#Choose anti-isolated region
	if reverseIsoCut:
		goodSignalElectronCut += '&& userFloat("rhoCorrRelIso") > 0.1 && userFloat("rhoCorrRelIso") < 0.5 '
	#Choose isolated region
	else:
		goodSignalElectronCut += '&& userFloat("rhoCorrRelIso") < 0.1'

	# goodQCDElectronCut = goodElectronCut
	# goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") > 0.2'
	# goodQCDElectronCut += '&& userFloat("rhoCorrRelIso") < 0.5'

	looseVetoElectronCut = "%s > 20" % electronPt
	looseVetoElectronCut += "&& abs(eta) < 2.5"
	#looseVetoElectronCut += "&& (0.0 < electronID('mvaTrigV0') < 1.0)"
	looseVetoElectronCut += "&& electronID('mvaTrigV0') > %f" % 0.1
	looseVetoElectronCut += '&& userFloat("rhoCorrRelIso") < 0.3'

	process.goodSignalElectrons = cms.EDFilter("CandViewSelector",
	  src=cms.InputTag("elesWithIso"), cut=cms.string(goodSignalElectronCut)
	)

	# process.goodQCDElectrons = cms.EDFilter("CandViewSelector",
	#   src=cms.InputTag("elesWithIso"), cut=cms.string(goodQCDElectronCut)
	# )

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

	#Loose veto electrons are always (semi)isolated.
	#In the isolated region we need exactly 0...1 loose veto ele AND 0 loose veto mu.
	#In the ANTI-isolated region, we must have 0 loose veto ele AND 0 loose veto mu.
	process.looseEleVetoEle = cms.EDFilter(
		"PATCandViewCountFilter",
		src=cms.InputTag("looseVetoElectrons"),
		minNumber=cms.uint32(1 if not reverseIsoCut else 0),
		maxNumber=cms.uint32(1 if not reverseIsoCut else 0),
	)
	process.looseMuVetoEle = cms.EDFilter(
		"PATCandViewCountFilter",
		src=cms.InputTag("looseVetoMuons"),
		minNumber=cms.uint32(0),
		maxNumber=cms.uint32(0),
	)

	if metType == "MET":
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
		process.metEleSequence = cms.Sequence(process.goodMETs*process.hasMET)
	elif metType == "MtW":
		process.eleAndMETMT = cms.EDProducer('CandTransverseMassProducer',
			collections=cms.untracked.vstring(["patMETs", "goodSignalElectrons"])
		)
		process.hasEleMETMT = cms.EDFilter('EventDoubleFilter',
			src=cms.InputTag("eleAndMETMT"),
			min=cms.double(40),
			max=cms.double(9999999)
		)
		process.metEleSequence = cms.Sequence(process.eleAndMETMT * process.hasEleMETMT)
	else:
		print "WARNING: MET type not recognized in electron channel"

	process.recoNuProducerEle = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
		leptonSrc=cms.InputTag("goodSignalLeptons"),
		bjetSrc=cms.InputTag("btaggedJets"),
		metSrc=cms.InputTag("goodMETs" if metType=="MET" else "patMETs"), #either patMETs if cutting on ele + MET transverse mass or goodMETs if cutting on patMETs->goodMets pt
	)

	if doDebug:
		process.oneIsoEleIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("IDoneIsoEle"))
		process.eleVetoIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("IDeleVeto"))
		process.metIDS = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("MET"))
		process.NJetIDs = cms.EDAnalyzer('EventIDAnalyzer', name=cms.untracked.string("NJet"))
		process.electronAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("elesWithIso"))
		process.electronVetoAnalyzer = cms.EDAnalyzer('SimpleElectronAnalyzer', interestingCollections=cms.untracked.VInputTag("looseVetoElectrons"))
		process.metAnalyzer = cms.EDAnalyzer('SimpleMETAnalyzer', interestingCollections=cms.untracked.VInputTag("patMETs"))

"""
Configures the electron path with full selection.
channel:	'sig' - runs on signal (t-channel or tbar channel). Generator level comparisons are turned on.
			'bkg' - runs on background (anything else). Generator level comparisons turned off.
"""
def ElectronPath(process, isMC, channel, doDebug=False):
	process.elePathPreCount = cms.EDProducer("EventCountProducer")

	process.efficiencyAnalyzerEle = cms.EDAnalyzer('EfficiencyAnalyzer'
	, histogrammableCounters = cms.untracked.vstring(["elePath"])
	, elePath = cms.untracked.vstring([
		"PATTotalEventsProcessedCount",
		"singleTopPathStep1ElePreCount",
		"singleTopPathStep1ElePostCount",
		"elePathPreCount",
		"elePathStepHLTsyncElePostCount",
		"elePathOneIsoElePostCount",
		"elePathLooseEleVetoElePostCount",
		"elePathLooseMuVetoElePostCount",
		"elePathNJetsPostCount",
		"elePathMetEleSequencePostCount",
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
		process.looseVetoElectrons *
		process.oneIsoEle *

		process.looseEleVetoEle *
		process.looseVetoMuons *
		process.looseMuVetoEle *

		process.jetSequence *
		process.nJets *

		process.metEleSequence *
		process.goodSignalLeptons *

		process.mBTags *

		process.topRecoSequenceEle *
		process.efficiencyAnalyzerEle
	)

	#Insert debugging modules for printout
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
			process.elePath.index(process.looseEleVetoEle),
			process.electronVetoAnalyzer
		)
		process.elePath.insert(
			process.elePath.index(process.looseEleVetoEle)+1,
			process.eleVetoIDs
		)
		process.elePath.insert(
			process.elePath.index(process.metEleSequence)+1,
			process.metIDS
		)
		process.elePath.insert(
			process.elePath.index(process.nJets)+1,
			process.NJetIDs
		)
		process.elePath.insert(
			process.elePath.index(process.metEleSequence),
			process.metAnalyzer
		)


	if isMC and channel=="sig":
		#Put the parton level study after the top reco sequence.
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
		"metEleSequence",
		"nJets",
		"mBTags"
		]
	)
