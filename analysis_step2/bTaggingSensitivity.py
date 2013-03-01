from anfw import *

ROOT.gROOT.cd()

h0 = ROOT.TH1F("h0", "h0", 10, -1, 1)
h = h0.Clone("h")
h_bcd = h0.Clone("h_bcd")
h_bcu = h0.Clone("h_bcu")
h_ld = h0.Clone("h_ld")
h_lu = h0.Clone("h_lu")

cut = Cuts.finalMu.cutStr

nonan = "&& bTagWeight_bTagWeightProducer == bTagWeight_bTagWeightProducer && bTagWeightSystBCDown_bTagWeightProducer == bTagWeightSystBCDown_bTagWeightProducer && bTagWeightSystBCUp_bTagWeightProducer == bTagWeightSystBCUp_bTagWeightProducer && bTagWeightSystLDown_bTagWeightProducer == bTagWeightSystLDown_bTagWeightProducer && bTagWeightSystLUp_bTagWeightProducer == bTagWeightSystLUp_bTagWeightProducer"


for weight in ["1", "bTagWeight_bTagWeightProducer", "bTagWeightSystBCDown_bTagWeightProducer", "bTagWeightSystBCUp_bTagWeightProducer", "bTagWeightSystLDown_bTagWeightProducer", "bTagWeightSystLUp_bTagWeightProducer"]:
    channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_{0}".format(weight), "{0}*{2}*({1})".format(lumiW, cut), "")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h", "bTagWeight_bTagWeightProducer*(%s)" % (cut), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_bcd", "bTagWeightSystBCDown_bTagWeightProducer*(%s)" % (cut), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_bcu", "bTagWeightSystBCUp_bTagWeightProducer*(%s)" % (cut), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_ld", "bTagWeightSystLDown_bTagWeightProducer*(%s)" % (cut), "SAME")
channels["T_t"].tree.Draw("cosThetaLightJet_cosTheta>>h_lu", "bTagWeightSystLUp_bTagWeightProducer*(%s)" % (cut), "SAME")
#h = h0.Subtract(h)
# h0 = ROOT.gROOT.Get("h0")
# h = ROOT.gROOT.Get("h")
# h_bcd = ROOT.gROOT.Get("h_bcd")
# h_bcu = ROOT.gROOT.Get("h_bcu")
# h_ld = ROOT.gROOT.Get("h_ld")
# h_lu = ROOT.gROOT.Get("h_lu")

#leg = legend("LU")
#leg.AddEntry(h0, "unweighted")
#leg.Draw()

h0.SetTitle("Sensitivity to b-tagging SF")
h0.SetStats(False)

i = 0
for h in [h0, h, h_bcd, h_bcu, h_ld, h_lu]:
    h.SetLineColor(colorList[i])
    h.SetLineWidth(2)
    i += 1
