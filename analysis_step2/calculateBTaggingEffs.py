from anfw import *
import pdb
import math

#cut = Cuts.mu + Cuts.MT + Cuts.mlnu + Cuts.jetRMS + Cuts.jetPt + Cuts.jets_1LJ + Cuts.etaLJ + Cuts.recoFState #Cut("1plusLJ", "_lightJetCount>=1")
cut = Cuts.mu + Cuts.MT + Cuts.mlnu + Cuts.jetRMS + Cuts.etaLJ + Cuts.recoFState + Cuts.jetPt + Cut("1plusLJ", "_lightJetCount>=1")
#cut = Cuts.mu + Cuts.MT
print cut

def effUnc(eff, count):
    return math.sqrt(eff*(1.0-eff)/count)

of = ROOT.TFile("bTaggingEffs.root", "RECREATE")
def calcBTaggingEff(channel):
    print "B-tagging effs for channel {0}".format(channel)
    of.cd()
    hTrueB_bDiscr = ROOT.TH1F("hTrueB_BDiscr_{0}".format(channel), "true b-jet b-discriminator distribution", 1000, -100, 40)
    hTrueC_bDiscr = ROOT.TH1F("hTrueC_BDiscr_{0}".format(channel), "true c-jet b-discriminator distribution", 1000, -100, 40)
    hTrueL_bDiscr = ROOT.TH1F("hTrueL_BDiscr_{0}".format(channel), "true l-jet b-discriminator distribution", 1000, -100, 40)
    ROOT.gROOT.cd()
    #cut = Cuts.finalMu
    channels[channel].tree.Draw(">>elist", cut.cutStr)
    elist = ROOT.gROOT.Get("elist")
    print "Number of events in selection: %d" % elist.GetN()

    lepCount = {-1:0, 0: 0, 1:0, 2:0, 3:0}

    sumBTaggedB = 0
    sumTrueB = 0

    sumBTaggedC = 0
    sumTrueC = 0

    sumBTaggedL = 0
    sumTrueL = 0

    nFailed = 0
    tree = channels[channel].tree
    for i in range(elist.GetN()):
        tree.GetEntry(elist.GetEntry(i))
        if (tree._btaggedTrueBJetCount == -1 or tree._trueBJetCount == -1 or
            tree._btaggedTrueCJetCount == -1 or tree._trueCJetCount == -1 or
            tree._btaggedTrueLJetCount == -1 or tree._trueLJetCount == -1
        ):
            nFailed += 1
            #print "Warning: anomalous event"
            continue

        nJets = tree._lightJetCount + tree._bJetCount
        for i in range(min(2, nJets)):
            partonFlavour = getattr(tree, "_goodJets_{0}_partonFlavour".format(i))
            bDiscriminator = getattr(tree, "_goodJets_{0}_bDiscriminator".format(i))
            if abs(partonFlavour)==5:
                hTrueB_bDiscr.Fill(bDiscriminator)
            elif abs(partonFlavour)==4:
                hTrueC_bDiscr.Fill(bDiscriminator)
            else:
                hTrueL_bDiscr.Fill(bDiscriminator)


        lepCount[tree._genLeptonsTCount] += 1

        sumBTaggedB += tree._btaggedTrueBJetCount
        sumTrueB += tree._trueBJetCount

        sumBTaggedC += tree._btaggedTrueCJetCount
        sumTrueC += tree._trueCJetCount

        sumBTaggedL += tree._btaggedTrueLJetCount
        sumTrueL += tree._trueLJetCount

    print ("jet counts (tagged | all): B: %d | %d" % (sumBTaggedB, sumTrueB)) + ("; C: %d | %d" % (sumBTaggedC, sumTrueC)) + ("; L: %d | %d" % (sumBTaggedL, sumTrueL))
    #print "Generated lepton counts: {0}".format(str(lepCount))

    eff_b = float(sumBTaggedB)/float(sumTrueB)
    eff_c = float(sumBTaggedC)/float(sumTrueC)
    eff_l = float(sumBTaggedL)/float(sumTrueL)

    sigma_eff_b = effUnc(eff_b, sumTrueB)
    sigma_eff_c = effUnc(eff_c, sumTrueC)
    sigma_eff_l = effUnc(eff_l, sumTrueL)

    print "nFailed = {0}".format(nFailed)
    def printEff(eff, sigma, flavour):
        print "eff_{3} = {0:.2E} (\sigma {1:.2E}) ({2:.1%})".format(eff, sigma, sigma/eff, flavour)
    printEff(eff_b, sigma_eff_b, "b")
    printEff(eff_c, sigma_eff_c, "c")
    printEff(eff_l, sigma_eff_l, "l")

    print 80*"-"
    of.Write()

    return {"eff_b": eff_b, "eff_c": eff_c, "eff_l": eff_l}

calcBTaggingEff("T_t")
calcBTaggingEff("WJets")
calcBTaggingEff("TTbar")

of.Close()
