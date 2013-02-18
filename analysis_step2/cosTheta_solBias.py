import ROOT
from anfw import *

r_ = (20, -1, 1)
canvFactor = 2.0

hTrue = channels["T_t"].plot1D("cosThetaLightJet_trueCosThetaProducerMu", r=r_, cut=Cuts.recoFState)
normalize(hTrue)
hTrue.SetLineColor(ROOT.kRed)
hTrue.SetLineWidth(2)

hMeas_all = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r_, cut=Cuts.recoFState)
normalize(hMeas_all)
hMeas_all.SetLineColor(ROOT.kBlue)
hMeas_all.SetLineWidth(1)

hMeas_real = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r_, cut=Cuts.recoFState+Cuts.realSol)
normalize(hMeas_real)
hMeas_real.SetLineColor(ROOT.kGreen+4)
hMeas_real.SetLineWidth(1)

hMeas_cplx = channels["T_t"].plot1D("cosThetaLightJet_cosThetaProducerMu", r=r_, cut=Cuts.recoFState+Cuts.cplxSol)
normalize(hMeas_cplx)
hMeas_cplx.SetLineColor(ROOT.kViolet)
hMeas_cplx.SetLineWidth(1)

c = ROOT.TCanvas()
c.SetWindowSize(int(canvFactor*1280), int(canvFactor*1024))
hTrue.GetYaxis().SetRangeUser(0, 0.1)
hTrue.SetStats(False)
hTrue.SetTitle("t-channel cosTheta* nu momentum sol. bias")
hTrue.GetXaxis().SetTitle("cosTheta*")

hTrue.Draw()
hMeas_all.Draw("SAME")
hMeas_real.Draw("SAME")
hMeas_cplx.Draw("SAME")

ks_real = hTrue.Chi2Test(hMeas_real, "WWCHI2/NDF")
ks_cplx = hTrue.Chi2Test(hMeas_cplx, "WWCHI2/NDF")
ks_all = hTrue.Chi2Test(hMeas_all, "WWCHI2/NDF")

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.SetTextSize(0.05)
leg.SetFillColor(ROOT.kWhite)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(hTrue, "gen")
leg.AddEntry(hMeas_all, "reco; #chi^{2}/NDF = %.2f" % ks_all)
leg.AddEntry(hMeas_real, "reco (real); #chi^{2}/NDF = %.2f" % ks_real)
leg.AddEntry(hMeas_cplx, "reco (cplx); #chi^{2}/NDF = %.2f" % ks_cplx)
leg.Draw()

c.Print("plot_cosTheta_sol_bias.png")