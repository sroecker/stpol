import ROOT
from anfw import *

r_ = (20, -1, 1)
canvFactor = 2.0

hTrue = channels["T_t"].plot1D("cosThetaLightJet_trueCosThetaProducerMu", r=r_)
normalize(hTrue)
hTrue.SetLineColor(ROOT.kRed)
hTrue.SetLineWidth(1)

hMeas_all = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r_, cut=Cuts.recoFState)
normalize(hMeas_all)
hMeas_all.SetLineColor(ROOT.kBlue)
hMeas_all.SetLineWidth(3)

hMeas_trueJet = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerTrueJetMu", r=r_)
normalize(hMeas_trueJet)
hMeas_trueJet.SetLineColor(ROOT.kGreen+4)
hMeas_trueJet.SetLineWidth(1)

hMeas_trueTop = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerTrueTopMu", r=r_)
normalize(hMeas_trueTop)
hMeas_trueTop.SetLineColor(ROOT.kViolet)
hMeas_trueTop.SetLineWidth(1)

ks_genAll = hMeas_all.Chi2Test(hTrue, "WWCHI2/NDF")
ks_genJet = hMeas_all.Chi2Test(hMeas_trueJet, "WWCHI2/NDF")
ks_genTop = hMeas_all.Chi2Test(hMeas_trueTop, "WWCHI2/NDF")

c = ROOT.TCanvas()
c.SetWindowSize(int(canvFactor*1280), int(canvFactor*1024))
hTrue.GetYaxis().SetRangeUser(0, 0.1)
hTrue.SetStats(False)
hTrue.SetTitle("t-channel cosTheta* reconstruction bias")
hTrue.GetXaxis().SetTitle("cosTheta*")

hTrue.Draw()
hMeas_all.Draw("SAME")
hMeas_trueJet.Draw("SAME")
hMeas_trueTop.Draw("SAME")

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(hMeas_all, "recoAll #chi^{2}/NDF=%.2f" % 0.0)
leg.AddEntry(hTrue, "genAll #chi^{2}/NDF=%.2f" % ks_genAll)
leg.AddEntry(hMeas_trueJet, "genJet #chi^{2}/NDF=%.2f" % ks_genJet)
leg.AddEntry(hMeas_trueTop, "genTop #chi^{2}/NDF=%.2f" % ks_genTop)
leg.Draw()

c.Print("plot_cosTheta_reco_bias.png")