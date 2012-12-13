import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.channel = Config.Channel.signal
Config.filterHLT = False

process = SingleTopStep2()
