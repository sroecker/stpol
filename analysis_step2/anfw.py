import ROOT
import sys

class Files:
	outFile = ROOT.TFile("outFile.root", "RECREATE")
	pass

class Cut:
	def __init__(self, cutName, cutStr):
		self.cutName = cutName
		self.cutStr = cutStr

	def __add__(self, other):
		cutName = self.cutName + "__" + other.cutName
		cutStr = self.cutStr + " && " + other.cutStr
		return Cut(cutName, cutStr)

class Cuts:
	recoFState = Cut("recoFstate", "cosThetaLightJet_cosThetaProducerMu==cosThetaLightJet_cosThetaProducerMu")
	realSol = Cut("realSol", "solType_recoNuProducerMu==0")
	cplxSol = Cut("cplxSol", "solType_recoNuProducerMu==1")
	signalRegion = Cut("signalRegion", "_recoTopMu_0_Mass>130&&_recoTopMu_0_Mass<220")
	sidebandRegion = Cut("sidebandRegion", "!(_recoTopMu_0_Mass>130&&_recoTopMu_0_Mass<220)")

class Channel:
	def __init__(self, channelName, fileName, crossSection):
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



	def plot1D(self, varName, r=[100, None, None], cut=None, fn="", weight=None):
		c = ROOT.TCanvas()
		c.SetBatch(True)
		if r[1] is None:
			r[1] = self.tree.GetMinimum(varName)
		if r[2] is None:
			r[2] = self.tree.GetMaximum(varName)
		if cut is None:
			cut = Cut("", "1==1")
		histName = varName + "_" + cut.cutName + "_" + fn + "_hist"
		h = ROOT.TH1F(histName, varName, r[0], r[1], r[2])

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
	"T_t": Channel("T_t", "data/stpol_T_t_trees.root", 47),
	"TTBar": Channel("TTBar", "data/stpol_TTBar_trees.root", 136.3)
}


def normalize(h, to=1.0):
	h.Sumw2()
	h.Scale(to/h.Integral())
	return h

def canvas(s):
	c = ROOT.TCanvas()
	c.SetCanvasSize(int(s*1280), int(s*1024))
	c.SetWindowSize(int(s*1280), int(s*1024))
	return c

def legend(corner=None):

	if corner is None:
		corner = "LU"

	if corner == "LU":
		coords = [0.13, 0.64, 0.28, 0.87]
	if corner == "RU":
		coords = [0.56, 0.64, 0.71, 0.87]

	leg = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])
	leg.SetTextSize(0.05)
	leg.SetFillColor(ROOT.kWhite)
	leg.SetLineColor(ROOT.kWhite)
	return leg
