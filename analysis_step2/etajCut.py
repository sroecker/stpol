import ROOT
import sys
from anfw import *

print sys.argv

r = (20, 0, 5)
s = 1.5

TTBar = Channel("TTBar", sys.argv[1], 0)
T_t = Channel("TTBar", sys.argv[2], 0)

h1 = TTBar.plot1D("_untaggedJets_0_Eta", fn="abs", r=r)
h2 = T_t.plot1D("_untaggedJets_0_Eta", fn="abs", r=r)
normalize(h1)
normalize(h2)

h1.SetLineColor(ROOT.kRed)
h1.SetStats(False)

h1.GetXaxis().SetTitle("|#eta_{j}|")
h1.SetTitle("2J1T final state |#eta_{j}| distribution (normalized to unit area)")
h1.SetLineWidth(4)
h2.SetLineWidth(4)

c = ROOT.TCanvas()
c.SetCanvasSize(int(s*1280), int(s*1024))

h1.Draw()
h2.Draw("SAME")

leg = ROOT.TLegend(0.62, 0.65, 0.77, 0.88)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(h1, "t#bar{t}")
leg.AddEntry(h2, "t-channel")
leg.Draw()
c.Print("plot_etajDistribution.png")