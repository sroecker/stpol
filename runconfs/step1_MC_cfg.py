from PhysicsTools.PatAlgos.patTemplate_cfg import *
from SingleTopPolarization.Analysis.selection_step1_cfg import SingleTopStep1

SingleTopStep1(process, doSkimming=True, isMC=True, doElectron=True, doMuon=True, maxLeptonIso=0.2)
