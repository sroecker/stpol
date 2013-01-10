## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *

# load the PAT config
process.load("PhysicsTools.PatAlgos.patSequences_cff")

from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
runMEtUncertainties(process,
	  electronCollection=cms.InputTag("selectedPatElectrons"),
      photonCollection=None,
      muonCollection=cms.InputTag("selectedPatMuons"),
      tauCollection=cms.InputTag("selectedPatTaus"),
      jetCollection=cms.InputTag("selectedPatJets")
)


from PhysicsTools.PatAlgos.tools.pfTools import *

postfix = ""
jetAlgo="AK5"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=True, postfix=postfix)


# Let it run
process.p = cms.Path(
    getattr(process,"patPF2PATSequence"+postfix)
)

process.source.fileNames = ["/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root"]
process.maxEvents.input = 100
process.out.fileName = 'patTuple_PF2PAT.root'
