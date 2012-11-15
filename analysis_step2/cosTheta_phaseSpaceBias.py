import ROOT
from anfw import *

r_ = (20, -1, 1)
canvFactor = 2.0

hTrue_all = channels["T_t"].plot1D("cosThetaLightJet_trueCosThetaProducerMu", r=r_)
normalize(hTrue_all)
hTrue_all.SetLineColor(ROOT.kRed)
hTrue_all.SetLineWidth(2)

hTrue_reco = channels["T_t"].plot1D("cosThetaLightJet_trueCosThetaProducerMu", r=r_, cut=Cuts.recoFState)
normalize(hTrue_reco)
hTrue_reco.SetLineColor(ROOT.kBlue)
hTrue_reco.SetLineWidth(2)

hTrue_recoSR = channels["T_t"].plot1D("cosThetaLightJet_trueCosThetaProducerMu", r=r_, cut=Cuts.recoFState+Cuts.signalRegion)
normalize(hTrue_recoSR)
hTrue_recoSR.SetLineColor(ROOT.kGreen+4)
hTrue_recoSR.SetLineWidth(2)

c = ROOT.TCanvas()
c.SetWindowSize(int(canvFactor*1280), int(canvFactor*1024))
hTrue_all.GetYaxis().SetRangeUser(0, 0.1)
hTrue_all.SetStats(False)
hTrue_all.SetTitle("t-channel cosTheta* phase space bias (gen.)")
hTrue_all.GetXaxis().SetTitle("cosTheta*")

ks = hTrue_all.Chi2Test(hTrue_reco, "WWCHI2/NDF")
ks_SR = hTrue_all.Chi2Test(hTrue_recoSR, "WWCHI2/NDF")

hTrue_all.Draw()
hTrue_reco.Draw("SAME")
hTrue_recoSR.Draw("SAME")

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(hTrue_all, "all phase space")
leg.AddEntry(hTrue_reco, "2J1T; #chi^{2}/NDF = %.2f" % ks)
leg.AddEntry(hTrue_recoSR, "2J1T, SR; #chi^{2}/NDF = %.2f" % ks_SR)
leg.Draw()

c.Print("plot_cosTheta_PS_bias.png")