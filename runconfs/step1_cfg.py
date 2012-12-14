import sys
from SingleTopPolarization.Analysis import args

isMC = args.inArgs("mc")
skim = args.inArgs("skim")
doMuon = args.inArgs("mu")
doElectron = args.inArgs("ele")
onGrid = args.inArgs("grid")
globalTag = args.getArg("GT", default="")

from PhysicsTools.PatAlgos.patTemplate_cfg import *
from SingleTopPolarization.Analysis.selection_step1_cfg import SingleTopStep1

SingleTopStep1(process, doSkimming=skim, isMC=isMC, doElectron=doElectron, doMuon=doMuon, onGrid=onGrid, globalTag=globalTag)
