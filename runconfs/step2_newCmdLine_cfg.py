import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.onGrid = False #use cmdline arguments, see selection_step2_cfg for details
process = SingleTopStep2()