import ROOT
from anfw import *

lumi = 15.0/0.001
cut = Cuts.recoFState + Cuts.signalRegion + Cut("etaj", "abs(_untaggedJets_0_Eta)>2.5")
r = (20, -1, 1)
h1 = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r, cut=cut, weight=channels["T_t"].xsWeight*lumi)
h2 = channels["TTBar"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r, cut=cut, weight=channels["TTBar"].xsWeight*lumi)

h1.SetLineColor(ROOT.kRed)
h1.SetFillColor(ROOT.kRed)

h2.SetLineColor(ROOT.kOrange)
h2.SetFillColor(ROOT.kOrange)

c = ROOT.TCanvas()
c.SetWindowSize(1280,1024)
stack = ROOT.THStack()
stack.SetTitle("MC cosTheta* in muon channel, L_{int}=15 fb^{-1}, %s" % cut.cutName)

stack.Add(h2)
stack.Add(h1)
stack.Draw("HIST F")

leg = ROOT.TLegend(0.15, 0.64, 0.30, 0.87)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(h2, "t#bar{t}")
leg.AddEntry(h1, "t-channel")
leg.Draw()

stack.GetHistogram().GetXaxis().SetTitle("cosTheta*")
stack.GetHistogram().GetYaxis().SetTitle("evts/%.2f" % (2.0/r[0]))
c.Print("cosTheta_weighted_%s.png" % cut.cutName)

print "t-channel: %f" % h1.Integral()
print "ttbar: %f" % h2.Integral()