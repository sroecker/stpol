import ROOT
import sys
import string
import random

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
    mu = Cut("mu", "_muonCount==1")
    ele = Cut("ele", "_electronCount==1")
    jets_2J1T = Cut("2J1T", "_lightJetCount==1 && _bJetCount==1")
    jets_2J0T = Cut("2J0T", "_lightJetCount==1 && _bJetCount==0")
    jets_3J1T = Cut("3J1T", "_lightJetCount==2 && _bJetCount==1")
    jets_3J2T = Cut("3J2T", "_lightJetCount==2 && _bJetCount==2")
    realSol = Cut("realSol", "solType_recoNuProducerMu==0")
    cplxSol = Cut("cplxSol", "solType_recoNuProducerMu==1")
    mlnu = Cut("ml#nu", "_recoTop_0_Mass>130&&_recoTop_0_Mass<220")
    etaLJ = Cut("#eta_{lj}", "abs(_fwdMostLightJet_0_Eta)>2.5")
    sidebandRegion = Cut("!ml#nu", "!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)")
    jetPt = Cut("jetPt", "_fwdMostLightJet_0_Pt > 60 && _highestBTagJet_0_Pt>60")
    jetEta = Cut("jetEta", "abs(_fwdMostLightJet_0_Eta) < 4.5 && abs(_highestBTagJet_0_Eta) < 4.5")
    jetRMS = Cut("jetRMS", "_fwdMostLightJet_0_rms < 0.025")
    met = Cut("jetRMS", "_muAndMETMT > 50 | _eleAndMETMT > 50")
    Orso = mlnu + jets_2J1T + jetPt + jetRMS + met + jetEta

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

    def plot1D(self, var, r=[100, None, None], cut=None, fn="", weight=None):
        c = ROOT.TCanvas()
        c.SetBatch(True)
        if r[1] is None:
            r[1] = self.tree.GetMinimum(varName)
        if r[2] is None:
            r[2] = self.tree.GetMaximum(varName)
        if cut is None:
            cut = Cut("", "1==1")
        histName = self.channelName + "_" + varName + "_" + cut.cutName + "_" + fn + "_hist"
        h = ROOT.TH1F(histName, varName, r[0], r[1], r[2])
        if not self.color is None:
            h.SetLineColor(self.color)
            h.SetFillColor(self.color)

        if weight is None:
            weight = self.xsWeight

        self.tree.Draw("{2}({0})>>{1}".format(varName, histName, fn), "%f*(%s)" % (weight, cut.cutStr))
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


channels = {
    "T_t": Channel("T_t", "../trees/T_t.root", 47.0, color=ROOT.kOrange),
    "Tbar_t": Channel("Tbar_t", "../trees/Tbar_t.root", 25.0, color=ROOT.kBlue),
    "TTBar": Channel("TTBar", "../trees/TTBar.root", 136.3, color=ROOT.kRed),
    "WJets/1000": Channel("WJets'", "../trees/TTBar.root", 30400.0/1000, color=ROOT.kGreen),
    "QCDMu": Channel("QCDMu'", "../trees/QCDMu.root", 1, color=ROOT.kGray)
}


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
        coords = [0.87, 0.12, 0.99, 0.90]
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

def channelComp(variable, cuts=None, fn="", r=[20,None, None], doStack=False, doNormalize=False, legPos="R"):
    hists = dict()
    title = varNamePretty(variable) + " in " + cuts.cutName + " norm. to 1/pb"
    for name, channel in channels.items():
        hists[name] = channel.plot1D(variable, cut=cuts, fn=fn, r=r)
        if doNormalize:
            hists[name] = normalize(hists[name])

    c = ROOT.TCanvas()
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
            if n != "T_t" and n != "Tbar_t":
                leg.AddEntry(h, n)
                stack.Add(h)
        stack.Add(hists["T_t"])
        leg.AddEntry(hists["T_t"], "T_t")
        stack.Add(hists["Tbar_t"])
        leg.AddEntry(hists["Tbar_t"], "Tbar_t")
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

    if doStack:
        return c, hists, stack, leg
    else:
        return c, hists


