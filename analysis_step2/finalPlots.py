from anfw import *

merge = [
		["tW", ".+_tW$"],
		["s", ".+_s$"],
		["t#bar{t}", "TTBar$"],
		["WJets", "WJets$"],
		#["QCD", "QCD.+"],
		["diboson", "WW|WZ|ZZ"],
		["t", ".+_t$"],
		]
a = channelComp("cosThetaLightJet_cosTheta", cuts=Cuts.finalEle, r=(10, -1, 1), doStack=True, mergeList=merge)
b =  channelComp("cosThetaLightJet_cosTheta", cuts=Cuts.finalMu, r=(10, -1, 1), doStack=True, mergeList=merge)
a[0].Print("../plots/cosTheta_finalEle.pdf")
b[0].Print("../plots/cosTheta_finalMu.pdf")