import FWCore.ParameterSet.Config as cms

def TopRecoSetup(process, leptonSource="goodSignal", bTagSource="btaggedJets", untaggedSource="untaggedJets", nuSource="recoNuProducer"):
	#Reconstruct the 4-momentum of the top quark by adding the momenta of the b-jet, the neutrino and the charged lepton

	eleSource = leptonSource + "Electrons"
	muSource = leptonSource + "Muons"


	process.recoTopEle = cms.EDProducer('SimpleCompositeCandProducer',
	    sources=cms.VInputTag([nuSource+"Ele", bTagSource, eleSource])
	)

	process.recoTopMu = cms.EDProducer('SimpleCompositeCandProducer',
	    sources=cms.VInputTag([nuSource+"Mu", bTagSource, muSource])
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
