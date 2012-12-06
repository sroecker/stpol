import ROOT
from anfw import *

chan = "T_t"
c = channels[chan]

ROOT.gROOT.cd()

N = 20
d = (2.0/float(N))

hists = []
means = ROOT.TVectorF(N)
sigmas = ROOT.TVectorF(N)
centers = ROOT.TVectorF(N)
canv = ROOT.TCanvas()
canv.SetBatch(True)
cut = Cuts.recoFState + Cuts.Orso
for n in range(0,N):
	low = -1.0 + n*d
	high = low + d
	center = (low + high)/2.0
	h = ROOT.TH1F("c%d" % n, "%.2f < cos #theta*_{gen} < %.2f" % (low, high), 20, -2, 2)
	c.tree.Draw("(cosThetaLightJet_cosTheta - cosThetaLightJet_cosThetaProducerTrueAll) >> c%d"%n,
		(cut + Cut("c%d"%n, "cosThetaLightJet_cosThetaProducerTrueAll>%f && cosThetaLightJet_cosThetaProducerTrueAll<%f" % (low, high))).cutStr)
	hists.append(h)
	means[n] = h.GetMean()
	sigmas[n] = h.GetRMS()
	centers[n] = center
canv.Close()

canv1 = canvas(1.0)
meanPlot = ROOT.TGraph(centers, means)
meanPlot.SetLineColor(ROOT.kRed)
meanPlot.SetFillColor(ROOT.kRed)
sigmaPlot = ROOT.TGraph(centers, sigmas)
sigmaPlot.SetLineColor(ROOT.kBlue)
sigmaPlot.SetFillColor(ROOT.kBlue)

leg = legend("RU")
leg.AddEntry(meanPlot, "mean")
leg.AddEntry(sigmaPlot, "RMS")

mg = ROOT.TMultiGraph()
mg.SetTitle("t-channel cos #theta*_{true} - cos #theta*_{gen} distribution bin-by-bin")
mg.Add(meanPlot)
mg.Add(sigmaPlot)
mg.Draw("AL*")
leg.Draw("SAME")
mg.GetXaxis().SetTitle("cos #theta*_{gen.}")
canv1.Print("../plots/cosTheta_Resol_Summary.pdf")

canv2 = canvas(3.0)
canv2.Divide(5,2,0,0)
for n in range(N):
	canv2.cd(n+1)
	normalize(hists[n])
	hists[n].SetStats(False)
	hists[n].GetXaxis().SetTitle("cos #theta*_{gen.}")
	hists[n].Draw("HIST L*")
canv2.Print("../plots/cosTheta_Resol_Distributions.pdf")


h = c.plot2D("cosThetaLightJet_cosTheta", "cosThetaLightJet_cosThetaProducerTrueAll", cut)
canv3 = canvas(1.0)
canv3.SetBatch(False)
h.SetStats(False)
h.SetTitle("t-channel cos #theta* correlation plot in the final selection")
h.GetXaxis().SetTitle("cos #theta*_{gen}")
h.GetYaxis().SetTitle("cos #theta*_{reco}")
h.Draw("colz")
canv3.Print("../plots/cosTheta_Correlation.pdf")


# +Cut("ct0", "(cosThetaLightJet_cosTheta> -1.0) && (cosThetaLightJet_cosTheta< (-1.0+0.2))")

# recoFState = Cut("recoFState", "_topCount==1")

# def diff(chan):
# 	hGen = channels[chan].plot1D("cosThetaLightJet_cosThetaProducerTrueAll", cut=recoFState)
# 	hReco = channels[chan].plot1D("cosThetaLightJet_cosTheta", cut=recoFState)
# 	hDiff = hGen.Clone()
# 	hDiff.SetName(chan +"_diff")
# 	hDiff.Add(hReco, -1.0)
# 	hDiff.Rebin(4)
# 	normalize(hDiff)
# 	return hDiff

# hDiff_T_t = diff("T_t")
# hDiff_Tbar_t = diff("Tbar_t")

# hDiff_Tbar_t.SetTitle("(cos #theta*_{gen} - cos #theta*_{reco})in t-channel MC")
# hDiff_Tbar_t.GetXaxis().SetTitle("cos #theta*")
# hDiff_Tbar_t.SetStats(False)

# hDiff_T_t.SetLineWidth(2)
# hDiff_Tbar_t.SetLineWidth(2)
# hDiff_Tbar_t.SetLineColor(ROOT.kRed)

# leg = legend("CU")
# leg.AddEntry(hDiff_T_t, "t-channel")
# leg.AddEntry(hDiff_Tbar_t, "#bar{t}-channel")


# c1 = canvas(1.0)
# hDiff_Tbar_t.Draw("HIST")
# hDiff_T_t.Draw("HIST SAME")
# leg.Draw()
# c1.Print("../plots/cosTheta_resol.png")
# c1.Close()

# def resp(cVal=0.0):
# 	hResp = channels["T_t"].plot1D("cosThetaLightJet_cosTheta", cut=recoFState+Cut("cos%f" % cVal, "abs(cosThetaLightJet_cosThetaProducerTrueAll-%f)<0.01" % cVal))
# 	normalize(hResp)
# 	hResp.Rebin(5)
# 	return hResp

# c2 = canvas(1.0)
# h1 = resp(0.0)
# h1.SetLineColor(ROOT.kRed)
# h1.SetLineWidth(2)
# h2 = resp(0.5)
# h2.SetLineColor(ROOT.kBlue)
# h2.SetLineWidth(2)
# h3 = resp(-0.5)
# h3.SetLineColor(ROOT.kGreen)
# h3.SetLineWidth(2)

# leg = legend("LU")
# leg.AddEntry(h1, "cos #theta*_{gen} = 0.0")
# leg.AddEntry(h2, "cos #theta*_{gen} = 0.5")
# leg.AddEntry(h3, "cos #theta*_{gen} = -0.5")
# h2.SetTitle("t-channel cos #theta* normalized reconstruction resolution")
# h2.SetStats(False)
# h2.GetXaxis().SetTitle("cos #theta* reconstructed")
# h2.Draw("hist")
# h1.Draw("hist SAME")
# h3.Draw("hist SAME")
# leg.Draw()
# c2.Print("../plots/cosTheta_reco_resol.png")