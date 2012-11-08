import FWCore.ParameterSet.Config as cms

def TopRecoSetup(process, leptonSource="goodSignal", bTagSource="btaggedJets", untaggedSource="untaggedJets", nuSource="recoNuProducer"):
	#Reconstruct the 4-momentum of the top quark by adding the momenta of the b-jet, the neutrino and the charged lepton

	eleSource = leptonSource + "Electrons"
	muSource = leptonSource + "Muons"

	process.recoNu = cms.EDProducer(
		 'CandRefCombiner',
		 sources=cms.untracked.vstring(["recoNuProducerMu", "recoNuProducerEle"]),
			 maxOut=cms.untracked.uint32(1),
			 minOut=cms.untracked.uint32(1)
	)

	process.recoTopEle = cms.EDProducer('SimpleCompositeCandProducer',
		sources=cms.VInputTag([nuSource+"Ele", bTagSource, eleSource])
	)

	process.recoTopMu = cms.EDProducer('SimpleCompositeCandProducer',
		sources=cms.VInputTag([nuSource+"Mu", bTagSource, muSource])
	)

	process.recoTop = cms.EDProducer('SimpleCompositeCandProducer',
		sources=cms.VInputTag(["recoNu", bTagSource, "goodSignalLeptons"])
	)

	#Calculate the cosTheta* between the untagged jet and the lepton in the top CM frame
	process.cosThetaProducerEle = cms.EDProducer('CosThetaProducer',
		topSrc=cms.InputTag("recoTopEle"),
		jetSrc=cms.InputTag(untaggedSource),
		leptonSrc=cms.InputTag(eleSource)
	)

	process.cosThetaProducerMu = cms.EDProducer('CosThetaProducer',
		topSrc=cms.InputTag("recoTopMu"),
		jetSrc=cms.InputTag(untaggedSource),
		leptonSrc=cms.InputTag(muSource)
	)

	process.cosTheta = cms.EDProducer('CosThetaProducer',
		topSrc=cms.InputTag("recoTop"),
		jetSrc=cms.InputTag(untaggedSource),
		leptonSrc=cms.InputTag("goodSignalLeptons")
	)

	process.topRecoSequenceMu = cms.Sequence(
      process.recoNuProducerMu *
      process.recoNu *
	  process.recoTopMu *
	  process.cosThetaProducerMu *
	  process.recoTop *
	  process.cosTheta
	)

	process.topRecoSequenceEle = cms.Sequence(
      process.recoNuProducerEle *
      process.recoNu *
	  process.recoTopEle *
	  process.cosThetaProducerEle *
	  process.recoTop *
	  process.cosTheta
	)
