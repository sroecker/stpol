import ROOT
import sys
f = ROOT.TFile(sys.argv[1])

t = f.Get("treesCands").Get("eventTree")
t.AddFriend(f.Get("treesDouble").Get("eventTree"))
t.AddFriend(f.Get("treesInt").Get("eventTree"))

c = ROOT.TCanvas()
t.Draw("_recoNuProducerMu_0_Eta:trueNeutrino_genParticleSelectorMu_0_Eta>>etaCorr", "_recoNuProducerMu_0_Eta==_recoNuProducerMu_0_Eta", "colz")

h_etaCorr = f.Get("etaCorr")
h_etaCorr.SetStats(False)
h_etaCorr.SetTitle("t-channel reco-#nu/gen-#nu #eta correlation")
h_etaCorr.GetYaxis().SetTitle("reco #eta")
h_etaCorr.GetXaxis().SetTitle("gen #eta")
c.Print("reco_gen_eta_corr.png")

h_recoEta = ROOT.TH1F("recoEta", "recoEta", 20, -5, 5)
h_genEta = ROOT.TH1F("genEta", "genEta", 20, -5, 5)

t.Draw("_recoNuProducerMu_0_Eta>>recoEta", "_recoNuProducerMu_0_Eta==_recoNuProducerMu_0_Eta")
t.Draw("trueNeutrino_genParticleSelectorMu_0_Eta>>genEta", "_recoNuProducerMu_0_Eta==_recoNuProducerMu_0_Eta")

c = ROOT.TCanvas()
h_recoEta.SetLineColor(ROOT.kRed)
h_genEta.SetLineColor(ROOT.kBlue)
h_recoEta.SetLineWidth(2)
h_genEta.SetLineWidth(2)
h_recoEta.SetStats(False)
h_recoEta.SetTitle("reco/gen #eta in reco fstate")
h_recoEta.GetXaxis().SetTitle("#eta")
h_recoEta.Draw()
h_genEta.Draw("SAME")

leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.AddEntry(h_recoEta, "reco #eta")
leg.AddEntry(h_genEta, "gen #eta")
leg.Draw()
c.Print("reco_gen_eta_distr.png")

def comparisonPlot(f, fn='', r=(-300, 300), col=ROOT.kRed, solType=-1):
	h_reco = ROOT.TH1F("reco"+f, "reco"+f, 50, r[0], r[1])
	h_gen = ROOT.TH1F("gen"+f, "gen"+f, 50, r[0], r[1])
	cut = "solType_recoNuProducerMu>%d" % solType
	t.Draw("{1}(_recoNuProducerMu_0_{0})>>reco{0}".format(f, fn), cut)
	t.Draw("{1}(trueNeutrino_genParticleSelectorMu_0_{0})>>gen{0}".format(f, fn), cut)
	h_gen.SetLineColor(col)
	h_reco.SetLineColor(col)
	h_gen.SetLineStyle(2)
	h_reco.SetStats(False)
	h_reco.Draw()
	h_gen.Draw("SAME")
	ks = h_reco.KolmogorovTest(h_gen)
	print ks
	return (h_reco, h_gen)


def maxBin(hists):
	return max(map(lambda x: x.GetMaximum(), hists))

c = ROOT.TCanvas()
c.SetCanvasSize(2000, 1500)
h1 = comparisonPlot("Px", r=[-300, 300], col=ROOT.kBlue)
h2 = comparisonPlot("Py", r=[-300, 300], col=ROOT.kGreen)
h3 = comparisonPlot("Pz", r=[-300, 300], col=ROOT.kRed)
h3[0].SetTitle("t-channel reco/gen #nu momentum, m_{W} constraint + analytic (P_{x} P_{y}) solution")
h3[0].GetXaxis().SetTitle("neutrino p_{i}")
h3[0].GetYaxis().SetRangeUser(0, maxBin(h1+h2+h3)*1.2)

h3[0].Draw()
h3[1].Draw("SAME")
h1[0].Draw("SAME")
h1[1].Draw("SAME")
h2[0].Draw("SAME")
h2[1].Draw("SAME")
leg = ROOT.TLegend(0.13, 0.64, 0.28, 0.87)
leg.AddEntry(h3[0], "pz reco")
leg.AddEntry(h3[1], "pz gen")
leg.AddEntry(h1[0], "px reco")
leg.AddEntry(h1[1], "px gen")
leg.AddEntry(h2[0], "py reco")
leg.AddEntry(h2[1], "py gen")
leg.Draw()
c.Print("nu_momentum.png")
c = ROOT.TCanvas()

def correlationPlot(fn, r=(-300, 300), solType=0):
	cut = "solType_recoNuProducerMu==%d" % solType
	t.Draw("_recoNuProducerMu_0_{0}:trueNeutrino_genParticleSelectorMu_0_{0}>>h".format(fn), cut)
	h = f.Get("h")
	h.SetName("corr%s" % fn)
	#print "Correlation %.2f" % h.GetCorrelationFactor()
	return h

for s in ["Px", "Py", "Pz"]:
 	h = correlationPlot(s, solType=0)
 	cor = h.GetCorrelationFactor()
 	cov = h.GetCovariance()
 	print "%s cor %.2f cov %.2f" % (s, cor, cov)


h0 = correlationPlot("Eta", solType=0)
h1 = correlationPlot("Eta", solType=1)

h0.SetTitle("eta correlation for real solution, corr=%.2f" % h0.GetCorrelationFactor())
h1.SetTitle("eta correlation for complex solution (cubic method), corr=%.2f" % h1.GetCorrelationFactor())
h0.SetStats(False)
h1.SetStats(False)

h0.GetXaxis().SetTitle("gen #eta")
h0.GetYaxis().SetTitle("reco #eta")
h1.GetXaxis().SetTitle("gen #eta")
h1.GetYaxis().SetTitle("reco #eta")
h0.Draw("colz")
c.Print("eta_corr_realsol.png")
h1.Draw("colz")
c.Print("eta_corr_complexsol.png")

N_real = float(t.GetEntries("solType_recoNuProducerMu==0"))
N_complex = float(t.GetEntries("solType_recoNuProducerMu==1"))
print "Complex fraction is %.2f" % (N_complex/(N_real+N_complex))