import sys
import ROOT
if "-b" in sys.argv:
	ROOT.gROOT.SetBatch(True)


def tb(batch, canv=None):
	if canv==None:
		ROOT.gROOT.SetBatch(batch)
	else:
		canv.SetBatch(batch)


def etaPlots():
	f = ROOT.TFile("out_step3_trees.root")
	print f
	trees = dict()

	trees["jets"] = f.Get("treesJets").Get("eventTree")
	trees["muons"] = f.Get("treesMu").Get("eventTree")

	t = trees["jets"]
	t.AddFriend(trees["muons"])
	ROOT.gROOT.cd()

	c = ROOT.TCanvas()
	tb(True, c)
	h0 = ROOT.TH1F("h0", "h0", 10, 0, 5)
	h1 = ROOT.TH1F("h1", "h1", 10, 0, 5)
	t.Draw("abs(goodJets_0_Eta)>>h0")
	t.Draw("abs(goodJets_1_Eta)>>h1")
	tb(False, c)
	c.Close()

	h0.SetLineColor(ROOT.kRed)
	h1.SetLineColor(ROOT.kBlue)

	c = ROOT.TCanvas()
	h0.Draw()
	h1.Draw("SAME")
	return c, h0, h1

def effCalcs():
	f = ROOT.TFile("effHist.root")

	histKeys = f.Get("efficiencyAnalyzer").GetListOfKeys()
	hists = [histKeys[i].GetName() for i in range(len(histKeys))]

	paths = dict()
	for hn in hists:
		h = f.Get("efficiencyAnalyzer").Get(hn)
		path = list()
		for i in range(1,h.GetNbinsX()+1):
			path.append(h.GetBinContent(i))
		paths[hn] = path
	f.Close()
	return paths

#A = etaPlots()
A = effCalcs()
muCounts = map(int, A["muPath"][-7:])
print("mu counts: " + ' | '.join('{0}'.format(k) for k in muCounts))
