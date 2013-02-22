import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.channel = Config.Channel.signal
Config.filterHLT = True
#Config.doDebug = True
Config.Jets.cutJets = True
#Config.Jets.source = "smearedPatJets"
Config.Jets.bTagDiscriminant = Config.Jets.BTagDiscriminant.CSV_MVA
Config.Jets.bTagWorkingPoint = Config.Jets.BTagWorkingPoint.CSVM

Config.Leptons.cutOnTransverseMass = True
process = SingleTopStep2()
