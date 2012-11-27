import sys
from SingleTopPolarization.Analysis import args

isMC = args.inArgs("mc")
filterHLT = args.inArgs("hlt")
doMuon = args.inArgs("mu")
doElectron = args.inArgs("ele")
nJets = args.getArg("nJ", default=2)
nBTags = args.getArg("nB", default=1)
antiIso = args.inArgs("antiIso")

if args.inArgs("sig"):
    channel = "sig"
else:
    channel = "bkg"

onGrid = args.inArgs("grid")
doDebug = args.inArgs("DEBUG")

import FWCore.ParameterSet.Config as cms
from SingleTopPolarization.Analysis.selection_step2_cfg import SingleTopStep2

process = SingleTopStep2(isMC=isMC, filterHLT=filterHLT, doMuon=doMuon, doElectron=doElectron, channel=channel, onGrid=onGrid, nJets=nJets, nBTags=nBTags, doDebug=doDebug, reverseIsoCut=antiIso)
