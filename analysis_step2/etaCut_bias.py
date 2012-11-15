import ROOT
from anfw import *

c = ROOT.TCanvas()
c.SetCanvasSize(1280, 1024)
Cuts.etajCut = Cut("etaj", "abs(_untaggedJets_0_Eta)>2.5")
h1 = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=(20,-1, 1), cut=(Cuts.etajCut+Cuts.recoFState+Cuts.signalRegion))
h2 = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=(20,-1, 1), cut=(Cuts.recoFState+Cuts.signalRegion))

h1.Sumw2()
h2.Sumw2()

h1.Scale(1.0/h1.Integral())
h2.Scale(1.0/h2.Integral())

ks_etaCut = h1.Chi2Test(h2, "WWCHI2/NDF")
h1.SetLineColor(ROOT.kRed)
h1.SetStats(False)
h1.SetLineWidth(3)
h2.SetLineWidth(3)
h1.SetTitle("normalized cosTheta* |#eta_{j}| bias, #chi^{2}/NDF=%.2f" % ks_etaCut)
h1.GetXaxis().SetTitle("cos #theta*")
h2.SetLineColor(ROOT.kBlue)
h1.Draw()
h2.Draw("SAME")
leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(h1, "2J1T, sig. reg.")
leg.AddEntry(h2, "2J1T, sig. reg., |#eta_{j}|>2.5   ")
leg.Draw()
c.Print("etajCut_bias.png")