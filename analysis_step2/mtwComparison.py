import ROOT
from anfw import *

lumi = 15.0/0.001

h1 = channels["T_t"].plot1D("_muAndMETMT", cut=Cuts.realSol, weight=channels["T_t"].xsWeight*lumi)
h2 = channels["T_t"].plot1D("_muAndMETMT", cut=Cuts.cplxSol, weight=channels["T_t"].xsWeight*lumi)
h1.SetLineColor(ROOT.kRed)
h2.SetLineColor(ROOT.kBlue)

c = canvas(0.6)

leg = legend("RU")
leg.AddEntry(h1, "real solution")
leg.AddEntry(h2, "complex solution")

h1.Draw()
h1.SetTitle("W transverse mass for real and complex neutrino momentum solution")
h1.SetStats(False)
h1.GetXaxis().SetTitle("M_{W,t}")
h2.Draw("SAME")
leg.Draw()
c.Print("plot_mtwComparison.png")