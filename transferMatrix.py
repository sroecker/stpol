import ROOT

f = ROOT.TFile("T_t_trees_v1.root")

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
