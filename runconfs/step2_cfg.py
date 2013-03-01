import sys
from SingleTopPolarization.Analysis import args
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2, Config

Config.isMC = args.inArgs("mc")
Config.filterHLT = args.inArgs("hlt")
Config.doMuon = args.inArgs("mu")
Config.doElectron = args.inArgs("ele")
Config.Jets.nJets = args.getArg("nJ", default=2)
Config.Jets.nBTags = args.getArg("nB", default=1)
Config.Leptons.reverseIsoCut = args.inArgs("antiIso")

if args.inArgs("sig"):
    Config.channel = Config.Channel.signal
else:
    Config.channel = Config.Channel.background

Config.onGrid = args.inArgs("grid")
Config.doDebug = args.inArgs("DEBUG")


process = SingleTopStep2()
