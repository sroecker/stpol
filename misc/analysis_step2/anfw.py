import ROOT
import sys
import string
import random
from cross_sections import xs
from collections import OrderedDict
import re
import argparse
import copy
import pdb
import logging


def h_str(self):

    integral = self.Integral(1, self.GetNbinsX())
    return "{0}: {1}, entries={2:.2E}, integral={5:.2E}, mean={3:.2E}, RMS={4:.2E}".format(
        type(self).__name__,
        self.GetName(),
        self.GetEntries(),
        self.GetMean(),
        self.GetRMS(),
        integral
    )

def makeStrSafe(s, badchars = ["{", "}", "+", "-", "."], replacement=""):
    for bc in badchars:
        s = s.replace(bc, replacement)
    return s

ROOT.TH1F.__str__ = h_str
ROOT.TH1D.__str__ = h_str
ROOT.TH1I.__str__ = h_str

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger("anfw")
if "-b" in sys.argv:
    sys.argv.remove("-b")

parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-d", "--datadir", type=str, default="./data/trees",
                    help="directory for the trees")
args = parser.parse_args()

lumi = 20000
sampleColors = {
    "T_t": ROOT.kRed,
    "Tbar_t": ROOT.kRed,
    "T_tW": ROOT.kYellow+4,
    "Tbar_tW": ROOT.kYellow+4,
    "T_s": ROOT.kYellow,
    "Tbar_s": ROOT.kYellow,

    "WJets": ROOT.kGreen,
    "W1Jets": ROOT.kGreen+1,
    "W2Jets": ROOT.kGreen+2,

    "WW": ROOT.kBlue,
    "WZ": ROOT.kBlue,
    "ZZ": ROOT.kBlue,

    "TTbar": ROOT.kOrange,

    "QCDMu": ROOT.kGray,

    "QCD_Pt_20_30_EMEnriched": ROOT.kGray,
    "QCD_Pt_30_80_EMEnriched": ROOT.kGray,
    "QCD_Pt_80_170_EMEnriched": ROOT.kGray,
    "QCD_Pt_170_250_EMEnriched": ROOT.kGray,
    "QCD_Pt_250_350_EMEnriched": ROOT.kGray,
    "QCD_Pt_350_EMEnriched": ROOT.kGray,


    "QCD_Pt_20_30_BCtoE": ROOT.kGray,
    "QCD_Pt_30_80_BCtoE": ROOT.kGray,
    "QCD_Pt_80_170_BCtoE": ROOT.kGray,
    "QCD_Pt_170_250_BCtoE": ROOT.kGray,
    "QCD_Pt_250_350_BCtoE": ROOT.kGray,
    "QCD_Pt_350_BCtoE": ROOT.kGray,

    "SingleMu": ROOT.kBlack,
    "SingleEle": ROOT.kBlack,
}

class Files:
    outFile = ROOT.TFile("outFile.root", "RECREATE")
    pass

class Cut:
    def __init__(self, cutName, cutStr):
        self.cutName = cutName
        self.cutStr = cutStr
        self.cutSequence = [copy.deepcopy(self)]

    def __add__(self, other):
        cutName = self.cutName + " + " + other.cutName
        cutStr = self.cutStr + " && " + other.cutStr
        newCut = Cut(cutName, cutStr)
        newCut.cutSequence = self.cutSequence + other.cutSequence
        return newCut

    def __str__(self):
        return self.cutName + ":" + self.cutStr

    def __repr__(self):
        return self.cutName


#Selection applied as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=228739
class Cuts:
    initial = Cut("postSkim", "1==1")

    recoFState = Cut("recoFstate", "_topCount==1")
    mu = Cut("mu", "_muonCount==1") + Cut("muIso", "_goodSignalMuons_0_relIso<0.12") + Cut("looseMuVeto", "_looseVetoMuCount==0") + Cut("looseEleVeto", "_looseVetoEleCount==0")
    ele = Cut("ele", "_electronCount==1") + Cut("eleIso", "_goodSignalElectrons_0_relIso<0.3") + Cut("eleMVA", "_goodSignalElectrons_0_mvaID>0.9")

    jets_1LJ = Cut("1LJ", "_lightJetCount==1")
    jets_2plusJ = Cut("1plusLJ", "_lightJetCount>=0 && _bJetCount>=0 && (_lightJetCount + _bJetCount)>=2")
    jets_2J1T = Cut("2J1T", "_lightJetCount==1 && _bJetCount==1")
    jets_2J0T = Cut("2J0T", "_lightJetCount==1 && _bJetCount==0")
    jets_3J1T = Cut("3J1T", "_lightJetCount==2 && _bJetCount==1")
    jets_3J2T = Cut("3J2T", "_lightJetCount==2 && _bJetCount==2")
    realSol = Cut("realSol", "solType_recoNuProducerMu==0")
    cplxSol = Cut("cplxSol", "solType_recoNuProducerMu==1")
    mlnu = Cut("ml#nu", "_recoTop_0_Mass>130&&_recoTop_0_Mass<220")
    etaLJ = Cut("#eta_{lj}", "abs(_lowestBTagJet_0_Eta)>2.5")
    sidebandRegion = Cut("!ml#nu", "!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)")
    jetPt = Cut("jetPt", "_goodJets_0_Pt>40 && _goodJets_1_Pt>40")
    jetEta = Cut("jetEta", "abs(_lowestBTagJet_0_Eta)<4.5 && abs(_highestBTagJet_0_Eta)<4.5")
    jetRMS = Cut("rms_{lj}", "_lowestBTagJet_0_rms < 0.025")
    MTmu = Cut("MT", "_muAndMETMT > 50")
    MTele = Cut("MT", "_patMETs_0_Pt>45")
#    Orso = mlnu + jets_2J1T + jetPt + jetRMS + MT + etaLJ#jetEta
    Orso = mlnu + jets_2J1T + jetPt + jetRMS + etaLJ + jetEta
    finalMu = mu + recoFState + Orso + MTmu
    finalEle = ele + recoFState + Orso + MTele

class Channel(object):
    def __init__(self, **kwargs):
        self.channelName = kwargs.get("channelName")
        self.fileName = kwargs.get("fileName")
        self.xs = kwargs.get("crossSection")
        self.color = kwargs.get("color")
        self.logger = logging.getLogger("anfw.Channel." + self.channelName)


        print "Opening file {0}".format(self.fileName)
        self.file = ROOT.TFile(self.fileName)
        self.integratedDataLumi = None

        self.effHistMu = self.file.Get("efficiencyAnalyzerMu").Get("muPath")
        self.effHistEle = self.file.Get("efficiencyAnalyzerEle").Get("elePath")

        #First bin contains the total number of processed events
        if self.xs>0:
            self.xsWeight = float(self.xs) / self.file.Get("efficiencyAnalyzerMu").Get("muPath").GetBinContent(1)
        else:
            self.xsWeight = 1


        keys = [x.GetName() for x in self.file.GetListOfKeys()]
        treeNames = filter(lambda x: x.startswith("tree"), keys)
        self.trees = [self.file.Get(k).Get("eventTree") for k in treeNames]
        if "flavourAnalyzer" in keys:
            self.trees.append(self.file.Get("flavourAnalyzer").Get("FlavorTree"))

        self.branches = []
        for t in self.trees[1:]:
            self.trees[0].AddFriend(t)
        for t in self.trees:
            branches = [x.GetName() for x in t.GetListOfBranches()]
            self.branches += branches
        self.tree = self.trees[0]

        print "processed events = {0}, passing mu skim = {1}, passing ele skim = {2}, in trees = {3}".format(
            self.effHistMu.GetBinContent(1),
            self.effHistMu.GetBinContent(3),
            self.effHistEle.GetBinContent(3),
            self.tree.GetEntriesFast()
        )

    def cutFlowOfCut(self, _cut):

        tempC = Cuts.initial
        print _cut
        print _cut.cutSequence
        for c in _cut.cutSequence:
            print "{0} ({1}) = {2}".format(tempC.cutName, tempC.cutStr, self.tree.GetEntries(tempC.cutStr))
            tempC += c
        return

    def cutFlowTotal(self):
        muHist = self.file.Get("efficiencyAnalyzerMu").Get("muPath")
        eleHist = self.file.Get("efficiencyAnalyzerEle").Get("elePath")
        cutFlowD = OrderedDict()
        for h in [muHist, eleHist]:
            for n in range(1, h.GetNbinsX()+1):
               cutFlowD[h.GetXaxis().GetBinLabel(n)] = int(h.GetBinContent(n))
        return cutFlowD

    """
    var - the name of the branch to plot
    varRange - [nbins, min, max] of the histogram
    additional kwargs:
    cut
    function
    varName
    """
    def plot1D(self, var, varRange, **kwargs):
        cut = kwargs.get("cut", Cuts.initial)
        varName = kwargs.get("varName")
        if varName is None:
            varName = varNamePretty(var)
        function = kwargs.get("function", "")
        integratedDataLumi = kwargs.get("integratedDataLumi")
        dtype = kwargs.get("dtype", "float")
        weight = kwargs.get("weight")

        self.logger.debug("var={0}, varRange={1}, kwargs={2}".format(var, varRange, kwargs))

        if weight is None:
            weight = 1.0

        histName = self.channelName + "_" + varName + "_" + cut.cutName + "_" + function + "_hist"
        histName = makeStrSafe(histName)
        if dtype=="float":
            h = ROOT.TH1F(histName, varName, varRange[0], varRange[1], varRange[2])
            h.Sumw2()
        elif dtype=="int":
            h = ROOT.TH1I(histName, varName, varRange[0], varRange[1], varRange[2])
        else:
            raise TypeError("Histogram type {0} not implemented".format(dtype))

        self.logger.debug("Created histogram '{0}'".format(h))

        c = ROOT.TCanvas()
        c.SetBatch(True)

        drawStr = "{2}({0})>>{1}".format(var, histName, function)
        weightStr = "%s*(%s)" % (weight, cut.cutStr)

        self.logger.debug("Calling TTree.Draw({0}, {1})".format(drawStr, weightStr))

        self.tree.Draw(drawStr, weightStr)
        self.logger.debug("Output histogram: {0}".format(h))

        nEntries = int(self.tree.GetEntries(cut.cutStr))
        if nEntries == 0 or h.GetEntries()==0 or h.Integral()==0:
            self.logger.warning("Histogram is empty: {0}".format(h))

        self.logger.info("True MC number of entries in cut {0} = {1:.2E}".format(cut.cutName, nEntries))
        self.styleHist(h)
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

    def styleHist(self, h):
        if not self.color is None:
            h.SetLineColor(self.color)
            h.SetFillColor(self.color)

class DataChannel(Channel):
    def __init__(self, **kwargs):
        super(DataChannel, self).__init__(**kwargs)
        self.lumi = kwargs.get("lumi")

    def styleHist(self, h):
        h.SetLineColor(self.color)
        h.SetFillColor(ROOT.kWhite)
        h.SetMarkerStyle(ROOT.kFullDotLarge)

class CombinedChannel(object):
    def __init__(self, **kwargs):
        self.channels = kwargs.get("channels")
        self.name = kwargs.get("name")
        self.chain = ROOT.TChain(self.name)
        for channel in self.channels:
            self.chain.Add(channel.file.GetName())

def loadSamples(enabledSamples):
    channels = OrderedDict()

    lumiPat = re.compile(".+_([0-9]*)_pb.*")
    for (sampleName, fileName) in enabledSamples.items():
        isData = "Single" in fileName


        if isData:
            samplexs = -1
        else:
            samplexs = xs[sampleName]
        if isData:
            lumiMatch = lumiPat.match(fileName)
            lumi = int(lumiMatch.group(1))
        if not isData:
            channels[sampleName] = Channel(
                channelName=sampleName,
                fileName=(args.datadir + "/" + fileName),
                crossSection=xs[sampleName],
                color=sampleColors[sampleName]
            )
        else:
            channels[sampleName] = DataChannel(
                channelName=sampleName,
                fileName=(args.datadir + "/" + fileName),
                crossSection=-1,
                color=ROOT.kBlack,
                lumi=lumi
            )
        cutFlowD = channels[sampleName].cutFlowTotal()
        print cutFlowD
    return channels

#channels["T_t"] = Channel("T_t", args.datadir + "/T_t.root", xs["T_t"], color=ROOT.kRed)
#channels["Tbar_t"] = Channel("Tbar_t", args.datadir + "/Tbar_t.root", xs["Tbar_t"], color=ROOT.kRed)
#channels["T_s"] = Channel("T_s", args.datadir + "/T_s.root", xs["T_s"], color=ROOT.kYellow)
#channels["Tbar_s"] = Channel("Tbar_s", args.datadir + "/Tbar_s.root", xs["Tbar_s"], color=ROOT.kYellow)
#channels["T_tW"] = Channel("T_tW", args.datadir + "/T_tW.root", xs["T_tW"], color=ROOT.kYellow+4)
#channels["Tbar_tW"] = Channel("Tbar_tW", args.datadir + "/Tbar_tW.root", xs["Tbar_tW"], color=ROOT.kYellow+4)
#channels["TTbar"] = Channel("TTbar", args.datadir + "/TTbar.root", xs["TTbar"], color=ROOT.kOrange)
#channels["WW"] = Channel("WW", args.datadir + "/WW.root", xs["WW"], color=ROOT.kBlue)
#channels["WZ"] = Channel("WZ", args.datadir + "/WZ.root", xs["WZ"], color=ROOT.kBlue)
#channels["ZZ"] = Channel("ZZ", args.datadir + "/ZZ.root", xs["ZZ"], color=ROOT.kBlue)
#channels["WJets"] = Channel("WJets", args.datadir + "/WD_WJets1.root", xs["WJets"], color=ROOT.kGreen)
#channels["W1Jets"] = Channel("W1Jets_excl", args.datadir + "/W1Jets.root", xs["WJets"], color=ROOT.kGreen)
#channels["SingleMu"] = Channel("SingleMu", args.datadir + "/SingleMu.root", -1, color=ROOT.kBlack)
#channels["QCDMu"] = Channel("QCDMu'", "/QCDMu.root", xs["QCDMu"], color=ROOT.kGray)
#channels["QCD_20_30_EM"] = Channel("QCD_20_30_EM", "/QCD_20_30_EM.root", xs["QCD_20_30_EM"], color=ROOT.kGray)
#channels["QCD_30_80_EM"] = Channel("QCD_30_80_EM", "/QCD_30_80_EM.root", xs["QCD_30_80_EM"], color=ROOT.kGray)
#channels["QCD_80_170_EM"] = Channel("QCD_80_170_EM", "/QCD_80_170_EM.root", xs["QCD_80_170_EM"], color=ROOT.kGray)
#channels["QCD_170_250_EM"] = Channel("QCD_170_250_EM", "/QCD_170_250_EM.root", xs["QCD_170_250_EM"], color=ROOT.kGray)
#channels["QCD_250_350_EM"] = Channel("QCD_250_350_EM", "/QCD_250_350_EM.root", xs["QCD_250_350_EM"], color=ROOT.kGray)
#    "QCD_350_EM": Channel("QCD_350_EM", "/QCD_350_EM.root", xs["QCD_350_EM"], color=ROOT.kGray),


def normalize(h, to=1.0):
    h.Sumw2()
    if h.Integral()>0.0:
        h.Scale(to/h.Integral())
    else:
        logger.warning("Histogram {0} is empty".format(h))
    return h

def canvas(s):
    name = randStr(4)
    c = ROOT.TCanvas(name, name)
    c.SetCanvasSize(int(s*1280), int(s*1024))
    c.SetWindowSize(int(1.05*s*1280), int(1.05*s*1024))
    return c

def randstr(n):
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
        coords = [0.72, 0.12, 0.99, 0.90]
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
    "_lowestBTagJet_0_Eta": "#eta_{lj}",
    "cosThetaLightJet_cosTheta": "cos #theta_{lj}",
    "_lightJetCount": "nJets",
    "_bJetCount": "nBTags",
    "nVerticesTrue_puWeightProducer": "N_{vtx. true.}",
    "_offlinePVCount": "N_{vtx. reco.}",
    "_muonsWithIso_0_normChi2": "muon norm. #chi^{2}",
    '_muonsWithIso_0_track_hitPattern_trackerLayersWithMeasurement': "muon track layers hit count",
    '_muonsWithIso_0_globalTrack_hitPattern_numberOfValidMuonHits': "muon global track hits",
    '_muonsWithIso_0_innerTrack_hitPattern_numberOfValidPixelHits': "muon inner track px hits",
    '_muonsWithIso_0_db': "muon db",
    '_muonsWithIso_0_dz': "muon dz",
    '_muonsWithIso_0_numberOfMatchedStations': "muon matched station count"
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

colorList = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kOrange, ROOT.kBlack, ROOT.kMagenta, ROOT.kYellow]


