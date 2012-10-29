import ROOT
import sys

fn = sys.argv[1]
f = ROOT.TFile(fn)

c = ROOT.TCanvas()
t = f.Get("treesDouble").Get("eventTree")
t.Draw("cosThetaLightJet_cosThetaProducerMu:cosThetaLightJet_trueCosThetaProducerMu>>h", "cosThetaLightJet_cosThetaProducerMu==cosThetaLightJet_cosThetaProducerMu")
h = f.Get("h")
h.SetStats(False)
h.SetTitle("Transfer matrix")
h.GetYaxis().SetTitle("cosTheta true")
h.GetXaxis().SetTitle("cosTheta measured")
h.Draw()
c.Print("transfer_matrix.png")


c = ROOT.TCanvas()
t.Draw("cosThetaLightJet_cosThetaProducerMu>>hmeas")
t.Draw("cosThetaLightJet_trueCosThetaProducerMu>>htrue")
hmeas = f.Get("hmeas")
htrue = f.Get("htrue")
hmeas.Scale(1.0/hmeas.Integral())
htrue.Scale(1.0/htrue.Integral())
hmeas.SetStats(False)
hmeas.SetTitle("normalized cosTheta* measured/true")
hmeas.SetLineColor(ROOT.kRed)
hmeas.GetXaxis().SetTitle("cosTheta*")
htrue.SetLineColor(ROOT.kBlue)

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.AddEntry(hmeas, "measured")
leg.AddEntry(htrue, "true")
hmeas.Draw()
htrue.Draw("SAME")
leg.Draw("SAME")
c.Print("cosTheta_meas_vs_true.png")
