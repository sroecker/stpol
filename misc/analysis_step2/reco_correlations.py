import ROOT
from anfw import *

canvFactor = 0.7
h_p_nu_x_all = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Px", "_recoNuProducerMu_0_Px", cut=Cuts.recoFState)
h_p_nu_y_all = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Py", "_recoNuProducerMu_0_Py", cut=Cuts.recoFState)
h_p_nu_z_all = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Pz", "_recoNuProducerMu_0_Pz", cut=Cuts.recoFState)

h_p_nu_x_real = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Px", "_recoNuProducerMu_0_Px", cut=Cuts.recoFState+Cuts.realSol)
h_p_nu_y_real = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Py", "_recoNuProducerMu_0_Py", cut=Cuts.recoFState+Cuts.realSol)
h_p_nu_z_real = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Pz", "_recoNuProducerMu_0_Pz", cut=Cuts.recoFState+Cuts.realSol)

h_p_nu_x_cplx = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Px", "_recoNuProducerMu_0_Px", cut=Cuts.recoFState+Cuts.cplxSol)
h_p_nu_y_cplx = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Py", "_recoNuProducerMu_0_Py", cut=Cuts.recoFState+Cuts.cplxSol)
h_p_nu_z_cplx = channels["T_t"].plot2D("trueNeutrino_genParticleSelectorMu_0_Pz", "_recoNuProducerMu_0_Pz", cut=Cuts.recoFState+Cuts.cplxSol)

c = ROOT.TCanvas()
c.SetWindowSize(int(canvFactor*1280), int(canvFactor*1024))
h_p_nu_z_cplx.SetStats(False)
h_p_nu_z_cplx.SetTitle("Complex p_{#nu,z} gen/reco correlation, C=%.2f" % h_p_nu_z_cplx.GetCorrelationFactor())
h_p_nu_z_cplx.Draw("colz")
c.Print("plot_p_nu_z_cplx.png")


h_p_nu_z_real.SetStats(False)
h_p_nu_z_real.SetTitle("Real p_{#nu,z} gen/reco correlation, C=%.2f" % h_p_nu_z_real.GetCorrelationFactor())
h_p_nu_z_real.Draw("colz")
c.Print("plot_p_nu_z_real.png")

for h in [h_p_nu_x_all, h_p_nu_y_all, h_p_nu_z_all, h_p_nu_x_real, h_p_nu_y_real, h_p_nu_z_real, h_p_nu_x_cplx, h_p_nu_y_cplx, h_p_nu_z_cplx]:
	print h.GetCorrelationFactor()

h_cosTheta_real = channels["T_t"].plot2D("cosThetaLightJet_trueCosThetaProducerMu", "cosThetaLightJet_cosThetaProducerMu", cut=Cuts.recoFState+Cuts.realSol)
h_cosTheta_real.SetTitle("T_t reco/gen particle cosTheta correlation, real sol., C = %.2f" % h_cosTheta_real.GetCorrelationFactor())
h_cosTheta_real.GetXaxis().SetTitle("reco cosTheta*")
h_cosTheta_real.GetYaxis().SetTitle("gen cosTheta*")
h_cosTheta_real.SetStats(False)
h_cosTheta_real.Draw("colz")
c.Print("plot_cosTheta_corr_real.png")

h_cosTheta_cplx = channels["T_t"].plot2D("cosThetaLightJet_trueCosThetaProducerMu", "cosThetaLightJet_cosThetaProducerMu", cut=Cuts.recoFState+Cuts.cplxSol)
h_cosTheta_cplx.SetTitle("T_t reco/gen particle cosTheta correlation, cplx sol., C = %.2f" % h_cosTheta_cplx.GetCorrelationFactor())
h_cosTheta_cplx.GetXaxis().SetTitle("reco cosTheta*")
h_cosTheta_cplx.GetYaxis().SetTitle("gen cosTheta*")
h_cosTheta_cplx.SetStats(False)
h_cosTheta_cplx.Draw("colz")
c.Print("plot_cosTheta_corr_cplx.png")

print "CosTheta real C = %.2f, N=%d" % (h_cosTheta_real.GetCorrelationFactor(), h_cosTheta_real.GetEntries())
print "CosTheta cplx C = %.2f, N=%d" % (h_cosTheta_cplx.GetCorrelationFactor(), h_cosTheta_cplx.GetEntries())

h_cosTheta_all = channels["T_t"].plot2D("cosThetaLightJet_trueCosThetaProducerMu", "cosThetaLightJet_cosThetaProducerMu", cut=Cuts.recoFState)
print "CosTheta all C = %.2f" % h_cosTheta_all.GetCorrelationFactor()
h_cosTheta_all.SetTitle("T_t reco/gen particle cosTheta correlation, C = %.2f" % h_cosTheta_all.GetCorrelationFactor())
h_cosTheta_all.GetXaxis().SetTitle("reco cosTheta*")
h_cosTheta_all.GetYaxis().SetTitle("gen cosTheta*")
h_cosTheta_all.SetStats(False)
h_cosTheta_all.Draw("colz")
c.Print("plot_cosTheta_corr_all.png")