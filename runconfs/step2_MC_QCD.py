import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.filterHLT = False
Config.channel = Config.Channel.background
Config.Leptons.reverseIsoCut = True

process = SingleTopStep2()
