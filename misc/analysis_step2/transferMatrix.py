import ROOT
import sys

fn = sys.argv[1]
f = ROOT.TFile(fn)

c = ROOT.TCanvas()
t = f.Get("treesDouble").Get("eventTree")
t.AddFriend(f.Get("treesCands").Get("eventTree"))
t.Draw("cosThetaLightJet_cosThetaProducerMu:cosThetaLightJet_trueCosThetaProducerMu>>h", "cosThetaLightJet_cosThetaProducerMu==cosThetaLightJet_cosThetaProducerMu")
h = f.Get("h")
h.SetStats(False)
h.SetTitle("CosTheta* correlation plot (transfer matrix)")
h.GetYaxis().SetTitle("cosTheta true")
h.GetXaxis().SetTitle("cosTheta measured")
h.Draw("colz")
c.Print("transfer_matrix.png")


c = ROOT.TCanvas()
hmeas = ROOT.TH1F("hmeas", "hmeas", 20, -1, 1)

htrueGenAll = ROOT.TH1F("htrueGenAll", "htrue", 20, -1, 1)
htrueGenTop = ROOT.TH1F("htrueGenTop", "htrueGenTop", 20, -1, 1)
htrueGenLepton = ROOT.TH1F("htrueGenLepton", "htrueGenLepton", 20, -1, 1)
htrueGenJet = ROOT.TH1F("htrueGenJet", "htrueGenJet", 20, -1, 1)

topConstraint = 40
sigRegion = "cosThetaLightJet_cosThetaProducerMu==cosThetaLightJet_cosThetaProducerMu && abs(_recoTopMu_0_Mass-170) < %f" % topConstraint
t.Draw("cosThetaLightJet_cosThetaProducerMu>>hmeas", sigRegion)
t.Draw("cosThetaLightJet_trueCosThetaProducerMu>>htrueGenAll", sigRegion)
t.Draw("cosThetaLightJet_cosThetaProducerTrueTopMu>>htrueGenTop", sigRegion)
t.Draw("cosThetaLightJet_cosThetaProducerTrueLeptonMu>>htrueGenLepton", sigRegion)
t.Draw("cosThetaLightJet_cosThetaProducerTrueJetMu>>htrueGenJet", sigRegion)


#KS tests
print hmeas.Integral()
ksprob_genAll = hmeas.KolmogorovTest(htrueGenAll)
ksprob_genTop = hmeas.KolmogorovTest(htrueGenTop)
ksprob_genLep = hmeas.KolmogorovTest(htrueGenLepton)
ksprob_genJet = hmeas.KolmogorovTest(htrueGenJet)

hmeas.SetStats(False)
hmeas.SetTitle("t-channel cos#theta* measured/true, #exists reco fstate, |M_{t_{meas}}-M_{t_{gen}}| < %.2f" % topConstraint)
hmeas.SetLineColor(ROOT.kRed)
htrueGenJet.SetLineColor(ROOT.kGreen)
htrueGenLepton.SetLineColor(ROOT.kOrange)
htrueGenTop.SetLineColor(ROOT.kViolet)
hmeas.GetXaxis().SetTitle("cos#theta*")
htrueGenAll.SetLineColor(ROOT.kBlue)
for h in [hmeas, htrueGenAll]:
	h.SetLineWidth(5)

for h in [htrueGenJet, htrueGenLepton, htrueGenTop]:
	h.SetLineWidth(3)
	h.SetLineStyle(2)

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.AddEntry(hmeas, "recoAll (measured) KS#equiv 1")
leg.AddEntry(htrueGenAll, "genAll (true) KS=%.2E" % ksprob_genAll)
leg.AddEntry(htrueGenJet, "genJet KS=%.2E" % ksprob_genJet)
leg.AddEntry(htrueGenTop, "genTop KS=%.2E" % ksprob_genTop)
leg.AddEntry(htrueGenLepton, "genLepton KS=%.2E" % ksprob_genLep)
hmeas.Draw()
htrueGenAll.Draw("SAME")
htrueGenJet.Draw("SAME")
htrueGenLepton.Draw("SAME")
htrueGenTop.Draw("SAME")
leg.Draw("SAME")
c.SetCanvasSize(3000,2000)
c.Print("cosTheta_meas_vs_true_topRange_%d.png" % topConstraint)
