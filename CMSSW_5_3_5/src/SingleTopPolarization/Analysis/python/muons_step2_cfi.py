import FWCore.ParameterSet.Config as cms
import SingleTopPolarization.Analysis.eventCounting as eventCounting

"""
This method configures the muon modules.
process: 		the process that obtain the modules (*modified by method*)
isMC:			'True' - running on MC
	   			'False' - running on data
muonSrc:		what collection to use for the initial pat::Muon-s
isoType:		'rhoCorrRelIso' - use the rho corrected relative isolation
				'deltaBetaCorrRelIso' - use delta beta corrected relative isolation
metType:		'MtW' - use the W transverse mass cut
				'MET' - use a simple MET cut
doDebug:		'True/False' - enable/disable debbuging modules with printout
reverseIsoCut:	'True' - choose anti-isolated leptons for QCD estimation
				'False' - choose isolated leptons for QCD estimation (default)
"""
def MuonSetup(process,
	isMC,
	muonSrc="muonsWithIso",
	isoType="rhoCorrRelIso",
	metType="MtW",
	doDebug=False,
	reverseIsoCut=False,
	applyIso=True,
	applyMET=False,
	met_cut=35
	):

	goodMuonCut = 'isPFMuon'																	   # general reconstruction property
	goodMuonCut += ' && isGlobalMuon'																   # general reconstruction property
	goodMuonCut += ' && pt > 26.'																	   # transverse momentum
	goodMuonCut += ' && abs(eta) < 2.1'																 # pseudo-rapisity range
	goodMuonCut += ' && normChi2 < 10.'																  # muon ID: 'isGlobalMuonPromptTight'
	goodMuonCut += ' && userFloat("track_hitPattern_trackerLayersWithMeasurement") > 5'							  # muon ID: 'isGlobalMuonPromptTight'
	goodMuonCut += ' && userFloat("globalTrack_hitPattern_numberOfValidMuonHits") > 0'							   # muon ID: 'isGlobalMuonPromptTight'
	goodMuonCut += ' && abs(dB) < 0.2'																  # 2-dim impact parameter with respect to beam spot (s. "PAT muon configuration" above)
	goodMuonCut += ' && userFloat("innerTrack_hitPattern_numberOfValidPixelHits") > 0'							   # tracker reconstruction
	goodMuonCut += ' && numberOfMatchedStations > 1'													# muon chamber reconstruction
	goodMuonCut += ' && abs(userFloat("dz")) < 0.5'
    goodSignalMuonCut = goodMuonCut

	looseVetoMuonCut = "isPFMuon"
	looseVetoMuonCut += "&& (isGlobalMuon | isTrackerMuon)"
	looseVetoMuonCut += "&& pt > 10"
	looseVetoMuonCut += "&& abs(eta)<2.5"
	looseVetoMuonCut += ' && userFloat("%s") < 0.2' % isoType  # Delta beta corrections (factor 0.5)
	looseVetoMuons += "&& !(%s)" % goodSignalMuonCut

	#Choose anti-isolated region

	if applyIso:
		if reverseIsoCut:
			goodSignalMuonCut += ' && userFloat("{0}") > 0.3 && userFloat("{0}") < 0.5'.format(isoType)
		#Choose isolated region
		else:
			goodSignalMuonCut += ' && userFloat("{0}") < 0.12'.format(isoType)

	process.goodSignalMuons = cms.EDFilter("CandViewSelector",
	  src=cms.InputTag(muonSrc), cut=cms.string(goodSignalMuonCut)
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

	process.muonCount = cms.EDProducer(
		"CollectionSizeProducer<reco::Candidate>",
        src = cms.InputTag("goodSignalMuons")
	)

	#in mu path we must have 1 loose muon (== THE isolated muon)
	#in the isolated region the signal muons and the loose veto muons overlap, thus we must have exactly 1 loose veto muon
	#in the anti-isolated region the signal muons are anti-isolated while the veto muons are isolated, thus there must be no loose veto muons
	process.looseMuVetoMu = cms.EDFilter(
		"PATCandViewCountFilter",
		src=cms.InputTag("looseVetoMuons"),
		minNumber=cms.uint32(1 if not reverseIsoCut else 0),
		maxNumber=cms.uint32(1 if not reverseIsoCut else 0),
	)

	#In Muon path we must have 0 loose electrons
	process.looseEleVetoMu = cms.EDFilter(
		"PATCandViewCountFilter",
		src=cms.InputTag("looseVetoElectrons"),
		minNumber=cms.uint32(0),
		maxNumber=cms.uint32(0),
	)



	#Either use MET cut or MtW cut
	if metType == "MET":
		met_cut=35
		process.goodMETs = cms.EDFilter("CandViewSelector",
		  src=cms.InputTag("patMETs"), cut=cms.string("pt>%f" % met_cut)
		)

		process.metMuSequence = cms.Sequence(
			process.goodMETs
		)

		if applyMET:
			process.hasMET = cms.EDFilter("PATCandViewCountFilter",
				src = cms.InputTag("goodMETs"),
				minNumber = cms.uint32(1),
				maxNumber = cms.uint32(1)
			)
			process.metMuSequence.insert(-1, process.hasMET)
			print "CUT\t applying MET cut %s" % mt_cut

	elif metType == "MtW":
		mt_cut=40

		#produce the muon and MET invariant transverse mass
		process.muAndMETMT = cms.EDProducer('CandTransverseMassProducer',
			collections=cms.untracked.vstring(["patMETs", "goodSignalMuons"])
		)

		process.metMuSequence = cms.Sequence(
			process.muAndMETMT
		)

		if applyMET:
			process.hasMuMETMT = cms.EDFilter('EventDoubleFilter',
				src=cms.InputTag("muAndMETMT"),
				min=cms.double(mt_cut),
				max=cms.double(9999999)
			)
			process.metMuSequence.insert(-1, process.hasMuMETMT)
			print "CUT\t applying MT cut %f" % mt_cut
	else:
		print "WARNING: MET type not specified!"

	process.recoNuProducerMu = cms.EDProducer('ClassicReconstructedNeutrinoProducer',
		leptonSrc=cms.InputTag("goodSignalLeptons"),
		bjetSrc=cms.InputTag("btaggedJets"),
		metSrc=cms.InputTag("goodMETs" if metType=="MET" else "patMETs"),
	)

def MuonPath(process, isMC, channel="sig"):

	print "muon path"
	print "CUT\tgoodSignalMuons=%s" % str(process.goodSignalMuons.cut)
	print "CUT\tlooseVetoMuons=%s" % str(process.looseVetoMuons.cut)
	print "CUT\tlooseVetoElectrons=%s" % str(process.looseVetoElectrons.cut)
	process.muPathPreCount = cms.EDProducer("EventCountProducer")

	process.efficiencyAnalyzerMu = cms.EDAnalyzer('EfficiencyAnalyzer'
	, histogrammableCounters = cms.untracked.vstring(["muPath"])
	, muPath = cms.untracked.vstring([
		"PATTotalEventsProcessedCount",
		"singleTopPathStep1MuPreCount",
		"singleTopPathStep1MuPostCount",
		"muPathPreCount",
		"muPathStepHLTsyncMuPostCount",
		"muPathOneIsoMuPostCount",
		"muPathLooseMuVetoMuPostCount",
		"muPathLooseEleVetoMuPostCount",
		"muPathNJetsPostCount",
		"muPathMetMuSequencePostCount",
		"muPathMBTagsPostCount"
		]
	))

	process.muPath = cms.Path(

		process.muonsWithIso *
		process.elesWithIso *

		process.muPathPreCount *

		#Optionally select the HLT
		process.stepHLTsyncMu *

		#Select one isolated muon and veto additional loose muon/electron
		process.goodSignalMuons *
		process.muonCount *
		#process.goodQCDMuons *
		process.looseVetoMuons *
		process.oneIsoMu *
		process.looseMuVetoMu *
		process.looseVetoElectrons *
		process.looseEleVetoMu *

		#Do general jet cleaning, PU-jet cleaning and select 2 good jets
		process.jetSequence *
		process.nJets *

		#Select mu and MET invariant transverse mass OR the MET
		process.metMuSequence *

		process.mBTags *

		#Reconstruct the neutrino, the top quark and calculate the cosTheta* variable
		process.topRecoSequenceMu *
		process.efficiencyAnalyzerMu
	)
	#if isMC:
	#	process.muPath.insert(process.muPath.index(process.noPUJets)+1, process.smearedJets)

	if isMC and channel=="sig":
		process.muPath.insert(
			process.muPath.index(process.topRecoSequenceMu)+1,
			process.partonStudyCompareSequence
		)

	#Count number of events passing the selection filters
	eventCounting.countAfter(process, process.muPath,
		[
		"stepHLTsyncMu",
		"oneIsoMu",
		"looseMuVetoMu",
		"looseEleVetoMu",
		"metMuSequence",
		"nJets",
		"mBTags"
		]
	)

