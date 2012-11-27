import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2

process = SingleTopStep2(isMC=True, filterHLT=True, doMuon=True, doElectron=True, channel='sig', cutJets=True, muonIsoType="deltaBetaCorrRelIso", eleMetType="MET")
