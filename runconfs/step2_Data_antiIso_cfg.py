import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2

process = SingleTopStep2(isMC=False, filterHLT=True, doMuon=True, doElectron=True, channel='bkg', onGrid=False, nJets=2, nBTags=1, doDebug=False, reverseIsoCut=True, cutJets=False)
