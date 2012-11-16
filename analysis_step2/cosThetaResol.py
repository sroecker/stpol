import ROOT
from anfw import *

recoFState = Cut("recoFState", "_topCount==1")

def diff(chan):
	hGen = channels[chan].plot1D("cosThetaLightJet_cosThetaProducerTrueAll", cut=recoFState)
	hReco = channels[chan].plot1D("cosThetaLightJet_cosTheta", cut=recoFState)
	hDiff = hGen.Clone()
	hDiff.SetName(chan +"_diff")
	hDiff.Add(hReco, -1.0)
	hDiff.Rebin(4)
	normalize(hDiff)
	return hDiff

hDiff_T_t = diff("T_t")
hDiff_Tbar_t = diff("Tbar_t")

hDiff_Tbar_t.SetTitle("(cos #theta*_{gen} - cos #theta*_{reco})in t-channel MC")
hDiff_Tbar_t.GetXaxis().SetTitle("cos #theta*")
hDiff_Tbar_t.SetStats(False)

hDiff_T_t.SetLineWidth(2)
hDiff_Tbar_t.SetLineWidth(2)
hDiff_Tbar_t.SetLineColor(ROOT.kRed)

leg = legend("CU")
leg.AddEntry(hDiff_T_t, "t-channel")
leg.AddEntry(hDiff_Tbar_t, "#bar{t}-channel")


c1 = canvas(1.0)
hDiff_Tbar_t.Draw("HIST")
hDiff_T_t.Draw("HIST SAME")
leg.Draw()
c1.Print("../plots/cosTheta_resol.png")
c1.Close()

def resp(cVal=0.0):
	hResp = channels["T_t"].plot1D("cosThetaLightJet_cosTheta", cut=recoFState+Cut("cos%f" % cVal, "abs(cosThetaLightJet_cosThetaProducerTrueAll-%f)<0.01" % cVal))
	normalize(hResp)
	hResp.Rebin(5)
	return hResp

c2 = canvas(1.0)
h1 = resp(0.0)
h1.SetLineColor(ROOT.kRed)
h1.SetLineWidth(2)
h2 = resp(0.5)
h2.SetLineColor(ROOT.kBlue)
h2.SetLineWidth(2)
h3 = resp(-0.5)
h3.SetLineColor(ROOT.kGreen)
h3.SetLineWidth(2)

leg = legend("LU")
leg.AddEntry(h1, "cos #theta*_{gen} = 0.0")
leg.AddEntry(h2, "cos #theta*_{gen} = 0.5")
leg.AddEntry(h3, "cos #theta*_{gen} = -0.5")
h2.SetTitle("t-channel cos #theta* normalized reconstruction resolution")
h2.SetStats(False)
h2.GetXaxis().SetTitle("cos #theta* reconstructed")
h2.Draw("hist")
h1.Draw("hist SAME")
h3.Draw("hist SAME")
leg.Draw()
c2.Print("../plots/cosTheta_reco_resol.png")