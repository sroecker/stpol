import ROOT
import sys
import string
import random
from cross_sections import xs
from collections import OrderedDict
import re

lumi = 20000

class Files:
    outFile = ROOT.TFile("outFile.root", "RECREATE")
    pass

class Cut:
    def __init__(self, cutName, cutStr):
        self.cutName = cutName
        self.cutStr = cutStr

    def __add__(self, other):
        cutName = self.cutName + " + " + other.cutName
        cutStr = self.cutStr + " && " + other.cutStr
        return Cut(cutName, cutStr)

class Cuts:
    recoFState = Cut("recoFstate", "_topCount==1")
    mu = Cut("mu", "_muonCount==1") + Cut("muIso", "_goodSignalMuons_0_relIso<0.12")
    ele = Cut("ele", "_electronCount==1") + Cut("eleIso", "_goodSignalElectrons_0_relIso<0.3") + Cut("eleMVA", "_goodSignalElectrons_0_mvaID>0.9")
    jets_2J1T = Cut("2J1T", "_lightJetCount==1 && _bJetCount==1")
    jets_2J0T = Cut("2J0T", "_lightJetCount==1 && _bJetCount==0")
    jets_3J1T = Cut("3J1T", "_lightJetCount==2 && _bJetCount==1")
    jets_3J2T = Cut("3J2T", "_lightJetCount==2 && _bJetCount==2")
    realSol = Cut("realSol", "solType_recoNuProducerMu==0")
    cplxSol = Cut("cplxSol", "solType_recoNuProducerMu==1")
    mlnu = Cut("ml#nu", "_recoTop_0_Mass>130&&_recoTop_0_Mass<220")
    etaLJ = Cut("#eta_{lj}", "abs(_lowestBTagJet_0_Eta)>2.5")
    sidebandRegion = Cut("!ml#nu", "!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)")
    jetPt = Cut("jetPt", "_goodJets_0_Pt>60 && _goodJets_1_Pt>60")
    jetEta = Cut("jetEta", "abs(_lowestBTagJet_0_Eta)<4.5 && abs(_highestBTagJet_0_Eta)<4.5")
    jetRMS = Cut("rms_{lj}", "_lowestBTagJet_0_rms < 0.025")
    MT = Cut("MT", "_muAndMETMT > 50 | _eleAndMETMT > 50")
    Orso = mlnu + jets_2J1T + jetPt + jetRMS + MT + etaLJ#jetEta
    finalMu = mu + recoFState + Orso
    finalEle = ele + recoFState + Orso

class Channel:
    def __init__(self, channelName, fileName, crossSection, color=None):
        self.channelName = channelName
        self.fileName = fileName
        self.xs = crossSection
        self.file = ROOT.TFile(fileName)
        self.xsWeight = float(self.xs) / self.file.Get("efficiencyAnalyzerMu").Get("muPath").GetBinContent(1)

        keys = [x.GetName() for x in self.file.GetListOfKeys()]
        treeNames = filter(lambda x: x.startswith("tree"), keys)
        self.trees = [self.file.Get(k).Get("eventTree") for k in treeNames]
        print keys
        if "flavourAnalyzer" in keys:
            self.trees.append(self.file.Get("flavourAnalyzer").Get("FlavorTree"))
        
        self.branches = []
        for t in self.trees[1:]:
            self.trees[0].AddFriend(t)
        for t in self.trees:
            branches = [x.GetName() for x in t.GetListOfBranches()]
            self.branches += branches
        self.tree = self.trees[0]
        if not color is None:
            self.color = color

    def cutFlow(self):
        muHist = self.file.Get("efficiencyAnalyzerMu").Get("muPath")
        eleHist = self.file.Get("efficiencyAnalyzerEle").Get("elePath")
        for h in [muHist, eleHist]:
            for n in range(1, h.GetNbinsX()+1):
                print "%s: %d" % (h.GetXaxis().GetBinLabel(n), int(h.GetBinContent(n)))

    def plot1D(self, var, r=[100, None, None], cut=None, fn="", weight=None, varName=None):
        c = ROOT.TCanvas()
        c.SetBatch(True)
        if r[1] is None:
            r[1] = self.tree.GetMinimum(varName)
        if r[2] is None:
            r[2] = self.tree.GetMaximum(varName)
        if cut is None:
            cut = Cut("", "1==1")
        if varName is None:
            varName = var
        histName = self.channelName + "_" + varName + "_" + cut.cutName + "_" + fn + "_hist"
        h = ROOT.TH1F(histName, varName, r[0], r[1], r[2])
        if not self.color is None:
            h.SetLineColor(self.color)
            h.SetFillColor(self.color)

        if weight is None:
            weight = lumi*self.xsWeight

        self.tree.Draw("{2}({0})>>{1}".format(varName, histName, fn), "%f*(%s)" % (weight, cut.cutStr))
        nEntries = int(self.tree.GetEntries(cut.cutStr))
        print "%s %s entries=%d" % (self.channelName, cut.cutName, nEntries)
        if nEntries<50:
            print "Histogram with very few entries, smoothing"
            h.Smooth(5)
        return h

    def plot2D(self, var1, var2, cut=None):
        c = ROOT.TCanvas()
        c.SetBatch(True)
        if cut is None:
            cut = Cut("", "1==1")
        histName = var1 + "_" + var2 + "_" + cut.cutName
        self.tree.Draw("{0}:{1}>>{2}".format(var1, var2, histName), cut.cutStr)
        h = ROOT.gROOT.CurrentDirectory().Get(histName)
        return h


channels = OrderedDict()

channels["T_t"] = Channel("T_t", "../trees/T_t.root", xs["T_t"], color=ROOT.kRed)
# channels["Tbar_t"] = Channel("Tbar_t", "../trees/Tbar_t.root", xs["Tbar_t"], color=ROOT.kRed)
# channels["T_s"] = Channel("T_s", "../trees/T_s.root", xs["T_s"], color=ROOT.kYellow)
# channels["Tbar_s"] = Channel("Tbar_s", "../trees/Tbar_s.root", xs["Tbar_s"], color=ROOT.kYellow)
# channels["T_tW"] = Channel("T_tW", "../trees/T_tW.root", xs["T_tW"], color=ROOT.kYellow+4)
# channels["Tbar_tW"] = Channel("Tbar_tW", "../trees/Tbar_tW.root", xs["Tbar_tW"], color=ROOT.kYellow+4)
channels["TTBar"] = Channel("TTBar", "../trees/TTBar.root", xs["TTBar"], color=ROOT.kOrange)
# channels["WW"] = Channel("WW", "../trees/WW.root", xs["WW"], color=ROOT.kBlue)
# channels["WZ"] = Channel("WZ", "../trees/WZ.root", xs["WZ"], color=ROOT.kBlue)
# channels["ZZ"] = Channel("ZZ", "../trees/ZZ.root", xs["ZZ"], color=ROOT.kBlue)
# channels["WJets"] = Channel("WJets'", "../trees/WJets.root", xs["WJets"], color=ROOT.kGreen)
# channels["QCDMu"] = Channel("QCDMu'", "../trees/QCDMu.root", xs["QCDMu"], color=ROOT.kGray)
# channels["QCD_20_30_EM"] = Channel("QCD_20_30_EM", "../trees/QCD_20_30_EM.root", xs["QCD_20_30_EM"], color=ROOT.kGray)
# channels["QCD_30_80_EM"] = Channel("QCD_30_80_EM", "../trees/QCD_30_80_EM.root", xs["QCD_30_80_EM"], color=ROOT.kGray)
# channels["QCD_80_170_EM"] = Channel("QCD_80_170_EM", "../trees/QCD_80_170_EM.root", xs["QCD_80_170_EM"], color=ROOT.kGray)
# channels["QCD_170_250_EM"] = Channel("QCD_170_250_EM", "../trees/QCD_170_250_EM.root", xs["QCD_170_250_EM"], color=ROOT.kGray)
# channels["QCD_250_350_EM"] = Channel("QCD_250_350_EM", "../trees/QCD_250_350_EM.root", xs["QCD_250_350_EM"], color=ROOT.kGray)
    #"QCD_350_EM": Channel("QCD_350_EM", "../trees/QCD_350_EM.root", xs["QCD_350_EM"], color=ROOT.kGray),


def normalize(h, to=1.0):
    h.Sumw2()
    h.Scale(to/h.Integral())
    return h

def canvas(s):
    name = randStr(4)
    c = ROOT.TCanvas(name, name)
    c.SetCanvasSize(int(s*1280), int(s*1024))
    c.SetWindowSize(int(1.05*s*1280), int(1.05*s*1024))
    return c

def randStr(n):
    chars = string.ascii_lowercase
    return ''.join([random.choice(chars) for i in range(n)])

def legend(corner=None):

    if corner is None:
        corner = "LU"

    if corner == "LU":
        coords = [0.13, 0.64, 0.28, 0.87]
    elif corner == "RU":
        coords = [0.79, 0.66, 0.94, 0.89]
    elif corner == "CU":
        coords = [0.42, 0.66, 0.58, 0.89]
    elif corner == "R":
        coords = [0.91, 0.12, 0.99, 0.90]
    elif corner == "RL":
        coords = [0.73, 0.20, 0.88, 0.43]

    leg = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])
    leg.SetTextSize(0.05)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetLineColor(ROOT.kWhite)
    return leg

def varNamePretty(varName):
    d = {
    "_recoTop_0_Mass": "ml#nu",
    "_fwdMostLightJet_0_Eta": "#eta_{lj}",
    "cosThetaLightJet_cosTheta": "cos #theta_{lj}",
    "_lightJetCount": "nJets",
    "_bJetCount": "nBTags"
    }
    if varName in d.keys():
        return d[varName]
    else:
        return varName

"""
Merges histograms in a dictionary according to the merge list, where
mergeList is a list in the format
[[name, regex], [name, regex], ...]
of the histograms to merge. The user is responsible for making the regex matches orthogonal.
returns an ordered dictionary of the merged histograms.
"""
def mergeHists(hists, mergeList=[]):
    oHists = OrderedDict()
    for (name, pattern) in mergeList:
        p = re.compile(pattern)
        matches = filter(lambda x: not p.search(x) is None, hists.keys())
        if len(matches)==0:
            print "No matches for {0}".format(pattern)
            continue
        oh = hists[matches[0]].Clone(name)
        print "Merging {0} to {1}".format(str(matches), name)
        for m in matches[1:]:
            oh.Add(hists[m])
        oHists[name] = oh
    return oHists




def channelComp(variable, cuts=None, fn="", r=[20,None, None], doStack=False, doNormalize=False, legPos="R", exclude="", mergeList=[]):
    hists = OrderedDict()
    title = varNamePretty(variable) + " in " + cuts.cutName + (" norm. to %.2f/fb" % (lumi/1000.0))
    for name, channel in channels.items():
        if len(exclude)>0:
            matches = re.findall(exclude, name)
            if len(matches)>0:
                print "Skipping {0}".format(name)
                continue

        hists[name] = channel.plot1D(variable, cut=cuts, fn=fn, r=r)

        if doNormalize:
            hists[name] = normalize(hists[name])

    c = ROOT.TCanvas()

    if len(mergeList)>0:
        hists = mergeHists(hists, mergeList)

    if not doStack:
        sortedHists = sorted(hists.items(), key=lambda x: x[1].Integral(), reverse=True)
    else:
        sortedHists = hists.items()

    for (n, h) in sortedHists:
        print "%s: %f" % (n, h.Integral())
    #sortedHists[0][1].Draw()

    leg = legend(legPos)
    if doStack:
        stack = ROOT.THStack()
        for (n, h) in sortedHists:
            leg.AddEntry(h, n)
            stack.Add(h)
        # stack.Add(hists["T_t"])
        # leg.AddEntry(hists["T_t"], "T_t")
        # stack.Add(hists["Tbar_t"])
        # leg.AddEntry(hists["Tbar_t"], "Tbar_t")
        stack.Draw("HIST F")
        leg.Draw()

        stack.GetHistogram().GetXaxis().SetTitle(varNamePretty(variable))
        stack.SetTitle(title)
    else:
        sortedHists[0][1].SetFillStyle(0)
        sortedHists[0][1].Draw("HIST")
        for n, h in sortedHists[1:]:
            h.Draw("HIST SAME")
            h.SetFillStyle(0)
    leg.SetTextSizePixels(3)

    if doStack:
        return c, hists, stack, leg
    else:
        return c, hists


