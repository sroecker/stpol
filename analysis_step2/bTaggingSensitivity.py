from anfw import *

ROOT.gROOT.cd()

h0 = ROOT.TH1F("h0", "h0", 10, -1, 1)
h = h0.Clone("h")
h_bcd = h0.Clone("h_bcd")
h_bcu = h0.Clone("h_bcu")
h_ld = h0.Clone("h_ld")
h_lu = h0.Clone("h_lu")

channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h0", "1*(%s)" % (Cuts.finalMu.cutStr), "")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h", "bTagWeight_bTagWeightProducer*(%s)" % (Cuts.finalMu.cutStr), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_bcd", "bTagWeightSystBCDown_bTagWeightProducer*(%s)" % (Cuts.finalMu.cutStr), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_bcu", "bTagWeightSystBCUp_bTagWeightProducer*(%s)" % (Cuts.finalMu.cutStr), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_ld", "bTagWeightSystLDown_bTagWeightProducer*(%s)" % (Cuts.finalMu.cutStr), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_lu", "bTagWeightSystLUp_bTagWeightProducer*(%s)" % (Cuts.finalMu.cutStr), "SAME")

# h0 = ROOT.gROOT.Get("h0")
# h = ROOT.gROOT.Get("h")
# h_bcd = ROOT.gROOT.Get("h_bcd")
# h_bcu = ROOT.gROOT.Get("h_bcu")
# h_ld = ROOT.gROOT.Get("h_ld")
# h_lu = ROOT.gROOT.Get("h_lu")

h0.SetTitle("Sensitivity to b-tagging SF")
h0.SetLineColor(2)
h.SetLineColor(3)
h_bcd.SetLineColor(4)
h_bcu.SetLineColor(5)
h_ld.SetLineColor(6)
h_lu.SetLineColor(7)

