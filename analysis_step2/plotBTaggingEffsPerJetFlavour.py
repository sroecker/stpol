import ROOT
f = ROOT.TFile("bTaggingEffs1.root")
import pdb
keys = map(lambda x: x.GetName(), f.GetListOfKeys())

colors = {"B": ROOT.kRed, "C":ROOT.kBlue, "L":ROOT.kGreen}
linestyle = {"T": 1, "WJets": 2, "TTbar": 9}
hue = {"T": 1, "WJets": 2, "TTbar": 3}

def getHistMax(hists):
	return max(map(lambda x: x.GetMaximum(), hists))

def plotInRange(x0, x1, rebinFactor=1):
	hists = dict()

	histArr = []
	for k in keys:
		flavour = k.split("_")[0][-1]
		channel = k.split("_")[2]
		if flavour not in hists.keys():
			hists[flavour] = dict()
		hists[flavour][channel] = f.Get(k)
		if (hists[flavour][channel].Integral()>0):
			hists[flavour][channel].Scale(1.0/hists[flavour][channel].Integral())
		hists[flavour][channel].Rebin(rebinFactor)
		hists[flavour][channel].SetLineColor(colors[flavour] + hue[channel])
		hists[flavour][channel].SetLineStyle(linestyle[channel])
		hists[flavour][channel].SetLineWidth(2)
		hists[flavour][channel].GetXaxis().SetRangeUser(x0, x1)
		histArr.append(hists[flavour][channel])

	c = ROOT.TCanvas()
	hists["B"]["T"].GetYaxis().SetRangeUser(0, getHistMax(histArr)*1.2)
	hists["B"]["T"].GetXaxis().SetTitle("b discriminator (TCHP)")
	hists["B"]["T"].Draw()
	hists["B"]["T"].SetStats(False)
	hists["B"]["T"].SetTitle("TCHP discriminator distribution by true parton flavour (norm.)")
	hists["B"]["TTbar"].Draw("SAME")
	hists["B"]["WJets"].Draw("SAME")

	hists["C"]["T"].Draw("SAME")
	hists["C"]["TTbar"].Draw("SAME")
	hists["C"]["WJets"].Draw("SAME")

	hists["L"]["T"].Draw("SAME")
	hists["L"]["TTbar"].Draw("SAME")
	hists["L"]["WJets"].Draw("SAME")

	leg = ROOT.TLegend(0.7, 0.5, 0.9, 0.9)
	for fl in ["C", "B", "L"]:
		for ch in ["T", "TTbar", "WJets"]:
			leg.AddEntry(hists[fl][ch], "{0} {1}".format(fl.lower(), ch))
	leg.SetFillColor(ROOT.kWhite)
	leg.SetLineColor(ROOT.kWhite)
	leg.Draw()
	#pdb.set_trace()
	c.Print("plots/bDiscriminatorByPartonFlavour_{0}_{1}.pdf".format(x0, x1))
	return

plotInRange(-5, 20, 5)
plotInRange(-100, -99)
plotInRange(-50, -5)