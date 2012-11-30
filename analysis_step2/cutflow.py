from anfw import *

for c in [Cuts.mu, Cuts.ele]:
	r1a = channelComp("_lightJetCount", cuts=c+Cuts.recoFState, r=(5, 0, 4), doStack=True)
	r1b = channelComp("_bJetCount", cuts=c+Cuts.recoFState, r=(5, 0, 4), doStack=True)
	r1a[0].Print("../plots/%s/cutflow_nJets.png" % c.cutName)
	r1b[0].Print("../plots/%s/cutflow_nBTags.png" % c.cutName)

	r2 = channelComp("_recoTop_0_Mass", cuts=c+Cuts.recoFState+Cuts.jets_2J1T, r=(20, 90, 400), doStack=True)
	r2[0].Print("../plots/%s/cutflow_topMass.png" % c.cutName)

	r3 = channelComp("_fwdMostLightJet_0_Eta", cuts=c+Cuts.recoFState+Cuts.jets_2J1T+Cuts.mlnu, fn="abs", r=(20, 0, 5), doStack=True)
	r3[0].Print("../plots/%s/cutflow_etaLJ.png" % c.cutName)

	r4 = channelComp("cosThetaLightJet_cosTheta", cuts=c+Cuts.recoFState+Cuts.jets_2J1T+Cuts.mlnu+Cuts.etaLJ, r=(20, -1, 1), doStack=True)
	r4[0].Print("../plots/%s/cutflow_cosThetaLJ.png" % c.cutName)
