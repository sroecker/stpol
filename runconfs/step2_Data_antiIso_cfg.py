import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.isMC = False
Config.Leptons.reverseIsoCut = True
Config.channel = Config.Channel.background

process = SingleTopStep2()
