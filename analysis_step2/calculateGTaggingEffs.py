from anfw import *

ROOT.gROOT.cd()
channels["T_t"].tree.Draw(">>elist"), Cuts.finalMu.cutStr)
elist = ROOT.gROOT.Get("elist")

sumBTaggedB = 0
sumTrueB = 0

sumBTaggedC = 0
sumTrueC = 0

sumBTaggedL = 0
sumTrueL = 0

for i in range(elist.GetN()):
	channels["T_t"].tree.GetEntry(elist.GetEntry(i))

	sumBTaggedB += channels["T_t"].tree._btaggedTrueBJetCount
	sumTrueB += channels["T_t"].tree._trueBJetCount

	sumBTaggedC += channels["T_t"].tree._btaggedTrueCJetCount
	sumTrueC += channels["T_t"].tree._trueCJetCount

	sumBTaggedL += channels["T_t"].tree._btaggedTrueLJetCount
	sumTrueL += channels["T_t"].tree._trueLJetCount

eff_b = float(sumBTaggedB)/float(sumTrueB)
eff_c = float(sumBTaggedC)/float(sumTrueC)
eff_l = float(sumBTaggedL)/float(sumTrueL)

print "eff_b = %.2E" % eff_b
print "eff_c = %.2E" % eff_c
print "eff_l = %.2E" % eff_l
