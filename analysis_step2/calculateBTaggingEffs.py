from anfw import *

channel = "T_t"

ROOT.gROOT.cd()
channels[channel].tree.Draw(">>elist", Cuts.finalMu.cutStr)
elist = ROOT.gROOT.Get("elist")
print "Number of events in selection: %d" % elist.GetN()

sumBTaggedB = 0
sumTrueB = 0

sumBTaggedC = 0
sumTrueC = 0

sumBTaggedL = 0
sumTrueL = 0

tree = channels[channel].tree
for i in range(elist.GetN()):
    tree.GetEntry(elist.GetEntry(i))
    if (tree._btaggedTrueBJetCount == -1 or tree._trueBJetCount == -1 or
        tree._btaggedTrueCJetCount == -1 or tree._trueCJetCount == -1 or
        tree._btaggedTrueLJetCount == -1 or tree._trueLJetCount == -1
    ):
        print "Warning: anomalous event"
        continue

    sumBTaggedB += tree._btaggedTrueBJetCount
    sumTrueB += tree._trueBJetCount

    sumBTaggedC += tree._btaggedTrueCJetCount
    sumTrueC += tree._trueCJetCount

    sumBTaggedL += tree._btaggedTrueLJetCount
    sumTrueL += tree._trueLJetCount

print "B: %d %d" % (sumBTaggedB, sumTrueB)
print "C: %d %d" % (sumBTaggedC, sumTrueC)
print "L: %d %d" % (sumBTaggedL, sumTrueL)

eff_b = float(sumBTaggedB)/float(sumTrueB)
eff_c = float(sumBTaggedC)/float(sumTrueC)
eff_l = float(sumBTaggedL)/float(sumTrueL)

print "eff_b = %.2E" % eff_b
print "eff_c = %.2E" % eff_c
print "eff_l = %.2E" % eff_l
