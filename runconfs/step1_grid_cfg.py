from PhysicsTools.PatAlgos.patTemplate_cfg import *
from SingleTopPolarization.Analysis.selection_step1_cfg import SingleTopStep1

SingleTopStep1(process, isMC=True, fileName="patTuple.root", doElectron=False)
