from anfw import *

ROOT.gROOT.SetBatch(True)
samples = {
    "TTbar_fast": Channel(channelName="TTbar_fast", fileName=args.datadir + "/TTJets_FSIM_FastSim.root", crossSection=1.0, color=sampleColors["TTbar"]+1),
    "TTbar_full": Channel(channelName="TTbar_full", fileName=args.datadir + "/TTJets_FSIM_FullSim.root", crossSection=1.0, color=sampleColors["TTbar"]+2),
}

"nVertices_puWeightProducer"

ROOT.gROOT.cd()
def plotComp(var, r, cut, varName=None, title="", filename=None):
    rs = randstr(4)
    h_fast = samples["TTbar_fast"].plot1D(var, r, cut=cut, weight=1.0, varName=varName)
    h_full = samples["TTbar_full"].plot1D(var, r, cut=cut, weight=1.0, varName=varName)
    h_fast.SetFillStyle(0)
    h_full.SetFillStyle(0)
    h_fast.SetLineWidth(2)
    h_full.SetLineWidth(2)
    h_fast.SetStats(False)
    h_full.SetStats(False)
    
    c = ROOT.TCanvas(rs, rs)
    h_fast.SetTitle(varName + title)
    h_fast.Draw("E1")
    h_full.Draw("E1 SAME")
    c.Show()
    if filename is not None:
        c.Print("plots/" + filename)
    return {"canvas": c, "h_fast": h_fast, "h_full": h_full}


#Vertices
regA = Cuts.jets_2J0T
res1 = plotComp("nVertices_puWeightProducer", [20, 0, 50], regA, varName="N_{vtx.}", title=" in 2J0T (muon+electron)")
res1["canvas"].Print("plots/fastSimValid_nGenVerts.png")

#Jet count in mu/ele
plotComp("_bJetCount + _lightJetCount", [5, 0, 4], Cuts.mu, varName="N_{jets}", title=" in muon channel", filename="fastSimValid_nJets_mu.png")
plotComp("_bJetCount + _lightJetCount", [5, 0, 4], Cuts.ele, varName="N_{jets}", title=" in electron channel", filename="fastSimValid_nJets_ele.png")

plotComp("_goodJets_0_Pt", [20, 0, 300], Cuts.mu, varName="p_{T} of 1. jet", title=" in muon channel", filename="fastSimValid_jet0pt_mu.png")
plotComp("abs(_goodJets_0_Eta)", [20, 0, 5], Cuts.mu, varName="|#eta| of 1. jet", title=" in muon channel", filename="fastSimValid_jet0eta_mu.png")

plotComp("_goodJets_1_Pt", [20, 0, 300], Cuts.mu, varName="p_{T} of 2. jet", title=" in muon channel", filename="fastSimValid_jet1pt_mu.png")
plotComp("abs(_goodJets_1_Eta)", [20, 0, 5], Cuts.mu, varName="|#eta| of 2. jet", title=" in muon channel", filename="fastSimValid_jet1eta_mu.png")

