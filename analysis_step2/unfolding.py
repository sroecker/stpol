import ROOT
from ROOT import RooUnfoldResponse
from ROOT import RooUnfold
from ROOT import RooUnfoldBayes
from ROOT import RooUnfoldSvd
from ROOT import RooUnfoldTUnfold
import sys

unfold = "unfold" in sys.argv

f = ROOT.TFile("~/Documents/stpol/trees/noSkim/T_t.root")
tree = f.Get("treesCands").Get("eventTree")

N = tree.GetEntries()
firstHalf = N/2

hMeas_test = ROOT.TH1D("hMeas_test", "measured", 20, -5, 5)
hTrue_test = ROOT.TH1D("hTrue_test", "true", 20, -5, 5)

if unfold:
	response = RooUnfoldResponse (20, -5, 5)
	for i in range(N/2):
		tree.GetEntry(i)
		xm = tree._recoTop_0_Eta
		xt = tree.trueTop_genParticleSelector_0_Eta
		if xm == xm and xt==xt:
			response.Fill(xm, xt)
		elif xm == xm and xt != xt:
			response.Fake(xm)
		elif xt == xt and xm != xm:
			response.Miss(xt)

for i in range(N/2, N):
	tree.GetEntry(i)
	xm = tree._recoTop_0_Eta
	xt = tree.trueTop_genParticleSelector_0_Eta
	if xm==xm:
		hMeas_test.Fill(xm)
	if xt==xt:
		hTrue_test.Fill(xt)

of = ROOT.TFile("out_unfold.root", "RECREATE" if unfold else "READ")

if unfold:
	unfoldBayes = RooUnfoldBayes(response, hMeas_test, 4, False, "bayes")
	kReg = 10 #Nbins/2
	unfoldSVD = RooUnfoldSvd(response, hMeas_test, kReg, 1000, "svd")
	unfoldTUnf = RooUnfoldTUnfold(response, hMeas_test, ROOT.TUnfold.kRegModeDerivative, "tunf")

	hRecoBayes = unfoldBayes.Hreco()
	hRecoSVD = unfoldSVD.Hreco()
	hRecoTUnf = unfoldTUnf.Hreco()
	of.Write()

else:
	hRecoBayes = of.Get("bayes")
	hRecoSVD = of.Get("svd")
	hRecoTUnf = of.Get("tunf")

c1 = ROOT.TCanvas("c1")
hTrue_test.SetTitle("Unfolding result")
hTrue_test.GetXaxis().SetTitle("#eta_{top}")
hTrue_test.SetStats(False)
hTrue_test.SetLineColor(ROOT.kRed)
hTrue_test.Draw()

hRecoSVD.SetLineColor(ROOT.kBlue)
hRecoBayes.SetLineColor(ROOT.kGreen)
hRecoTUnf.SetLineColor(ROOT.kMagenta)
hRecoSVD.Draw("SAME")
hRecoBayes.Draw("SAME")
hRecoTUnf.Draw("SAME")
leg = ROOT.TLegend(0.85, 0.61, 0.98, 0.88)
leg.SetFillColor(ROOT.kWhite)
leg.AddEntry(hTrue_test, "true'")
leg.AddEntry(hRecoSVD, "SVD")
leg.AddEntry(hRecoBayes, "Bayes")
leg.AddEntry(hRecoTUnf, "TUnfold")
leg.Draw()
c1.Print("../plots/unfoldingResult.png")


c2 = ROOT.TCanvas("c2")
nTrue = hTrue_test.Integral()
nMeas = hMeas_test.Integral()
hTrue_test.Scale(1.0/nTrue)
hMeas_test.Scale(1.0/nMeas)
hMeas_test.SetTitle("True vs. measured distributions (normalized)")
hMeas_test.SetStats(False)
hMeas_test.GetXaxis().SetTitle("#eta_{top}")
hMeas_test.Draw()
hTrue_test.Draw("SAME")
leg = ROOT.TLegend(0.71, 0.61, 0.98, 0.88)
leg.SetFillColor(ROOT.kWhite)
leg.AddEntry(hTrue_test, "true N = %d" % nTrue)
leg.AddEntry(hMeas_test, "measured N = %d" % nMeas)
leg.Draw()
c2.Print("../plots/unfoldingTruevsMeas.png")
