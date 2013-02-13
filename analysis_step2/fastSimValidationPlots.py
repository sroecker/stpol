from anfw import *
import pdb

lumi = 1

logger = logging.getLogger("fastSimValidationPlots")

ROOT.gROOT.SetBatch(True)
samples = {
    "TTbar_fast": Channel(channelName="TTbar_fast", fileName=args.datadir + "/TTJets_FastSim.root", crossSection=xs["TTbar"], color=ROOT.kRed),
    "TTbar_full": Channel(channelName="TTbar_full", fileName=args.datadir + "/TTJets_FullSim.root", crossSection=xs["TTbar"], color=ROOT.kGreen),
}
ROOT.gROOT.cd()

def plotComp(var, r, cut, varName=None, title="", filename=None, weight=1.0, normalization="MC", dtype="float"):
    rs = randstr(4)

    if weight=="PUWeight_puWeightProducer":
        title += ", PU reweighted"
        
    if normalization=="lumi":
        def weightStr(x):
            return "%f*%s" % (x, weight)
        title += ", [events/pb/u]"

    elif normalization=="MC":
        def weightStr(x):
            return "%s" % weight
        title += ", [MC events/u]"

    elif normalization=="unity":
        def weightStr(x):
            return "1"
        title += ", [norm. to unit area]"

    h_fast = samples["TTbar_fast"].plot1D(var, r, cut=cut, weight=weightStr(lumi*samples["TTbar_fast"].xsWeight), varName=varName, dtype=dtype)
    h_full = samples["TTbar_full"].plot1D(var, r, cut=cut, weight=weightStr(lumi*samples["TTbar_full"].xsWeight), varName=varName, dtype=dtype)
    h_fast.SetFillStyle(3004)
    h_full.SetFillStyle(3003)
    h_fast.SetLineWidth(2)
    h_full.SetLineWidth(2)
    h_fast.SetStats(False)
    h_full.SetStats(False)
    
    if normalization=="unity":
        normalize(h_fast)
        normalize(h_full)

    c = ROOT.TCanvas(rs, rs)
    c.SetCanvasSize(1280,1024)
    h_fast.SetTitle(varName + title)
    if normalization=="unity":
        normalize(h_fast)
        normalize(h_full)
    
    h_fast.GetXaxis().SetTitle(varName)
    logger.debug("Drawing histogram {0}".format(h_fast))
    h_fast.Draw("H1")
    logger.debug("Drawing histogram {0}".format(h_full))
    h_full.Draw("H1 SAME")
    leg = legend("LU")
    leg.SetFillStyle(4000)


    legEventsFull = ""
    legEventsFast = ""
    if normalize == "MC":
        legEventsFast = "{0:.2E} MC ev.".format(h_fast.Integral())
        legEventsFull = "{0:.2E} MC ev.".format(h_full.Integral())
    elif normalize == "":
        legEventsFast = "{0:.2E} ev./pb".format(h_fast.Integral())
        legEventsFull = "{0:.2E} ev./pb".format(h_full.Integral())

    leg.AddEntry(h_fast, "FastSim t#bar{t}" + legEventsFast)
    leg.AddEntry(h_full, "FullSim t#bar{t}" + legEventsFull)
    leg.Draw()
    c.Show()
    if filename is not None:
        c.Print("plots/" + filename)
    return {"canvas": c, "h_fast": h_fast, "h_full": h_full, "leg": leg}

cutNVtxA = Cut("nVtx_0_15", "nVertices_puWeightProducer>=0 && nVertices_puWeightProducer< 15")
cutNVtxB = Cut("nVtx_15_30", "nVertices_puWeightProducer>=15 && nVertices_puWeightProducer< 30")
cutNVtxC = Cut("nVtx_30_50", "nVertices_puWeightProducer>=30 && nVertices_puWeightProducer< 50")
baseCut = Cuts.initial# + cutNVtxB
leptonCut = Cuts.mu
#defaultWeight = "1"
defaultWeight = "PUWeight_puWeightProducer"

#Vertices
nVertRange = [20, 0, 50]
plotComp("nVertices_puWeightProducer", nVertRange, Cuts.initial, varName="N_{vtx.gen.}", title=" after skim (muon+electron)", filename="fastSimValid_nVerts_unweighted.png")
plotComp("nVertices_puWeightProducer", nVertRange, Cuts.initial, varName="N_{vtx.gen.}", title=" after skim (muon+electron)", filename="fastSimValid_nVerts_weighted.png", weight=defaultWeight)
plotComp("_offlinePVCount", nVertRange, Cuts.initial, varName="N_{vtx.reco.}", title=" after skim (muon+electron)", filename="fastSimValid_nVertsOffline_unweighted.png")
plotComp("_offlinePVCount", nVertRange, Cuts.initial, varName="N_{vtx.reco.}", title=" after skim (muon+electron)", filename="fastSimValid_nVertsOffline_weighted.png", weight=defaultWeight)

#Leptons
plotComp("_muonsWithIso_0_Pt", [20, 0, 150], baseCut, varName="muon p_{T}", title=" after skimming, before lepton ID", filename="fastSimValid_mu_pt_weighted.png", weight=defaultWeight, normalization="unity")
plotComp("abs(_muonsWithIso_0_Eta)", [20, 0, 2.6], baseCut, varName="muon |#eta|", title=" after skimming, before lepton ID", filename="fastSimValid_mu_eta_weighted.png", weight=defaultWeight, normalization="unity")

#Jet count in mu/ele
hi = plotComp("_bJetCount + _lightJetCount", [10, 0, 9], baseCut+leptonCut + Cut("jetOK", "_bJetCount>=0 && _lightJetCount>=0"), varName="N_{jets}", title=" in muon channel", filename="fastSimValid_nJets_mu.png", weight=defaultWeight, dtype="float", normalization="unity")

#Jet pt/eta in mu/ele
plotComp("_goodJets_0_Pt", [20, 0, 300], baseCut+leptonCut, varName="p_{T} of 1. jet", title=" in muon channel", filename="fastSimValid_jet0pt_mu.png", weight=defaultWeight, normalization="unity")
plotComp("abs(_goodJets_0_Eta)", [20, 0, 5], baseCut+leptonCut, varName="|#eta| of 1. jet", title=" in muon channel", filename="fastSimValid_jet0eta_mu.png", weight=defaultWeight, normalization="unity")

plotComp("_goodJets_1_Pt", [20, 0, 300], baseCut+leptonCut, varName="p_{T} of 2. jet", title=" in muon channel", filename="fastSimValid_jet1pt_mu.png", weight=defaultWeight, normalization="unity")
plotComp("abs(_goodJets_1_Eta)", [20, 0, 5], baseCut+leptonCut, varName="|#eta| of 2. jet", title=" in muon channel", filename="fastSimValid_jet1eta_mu.png", weight=defaultWeight, normalization="unity")

#Jet bDisriminator TCHP in mu & >=2J
plotComp("_goodJets_0_bDiscriminatorTCHP", [20, 0, 1], baseCut+leptonCut+Cuts.jets_2plusJ, varName="TCHP b-discr. of 1. jet", title=" in muon channel, >=2J", filename="fastSimValid_jet0_bDiscrTCHP.png", weight=defaultWeight, normalization="unity")
plotComp("_goodJets_1_bDiscriminatorTCHP", [20, 0, 1], baseCut+leptonCut+Cuts.jets_2plusJ, varName="TCHP b-discr. of 2. jet", title=" in muon channel, >=2J", filename="fastSimValid_jet1_bDiscrTCHP.png", weight=defaultWeight, normalization="unity")
plotComp("_goodJets_0_bDiscriminatorCSV_MVA", [20, 0, 1], baseCut+leptonCut+Cuts.jets_2plusJ, varName="CSV MVA b-discr. of 1. jet", title=" in muon channel, >=2J", filename="fastSimValid_jet0_bDiscrCSVMVA.png", weight=defaultWeight, normalization="unity")
plotComp("_goodJets_1_bDiscriminatorCSV_MVA", [20, 0, 1], baseCut+leptonCut+Cuts.jets_2plusJ, varName="CSV MVA b-discr. of 2. jet", title=" in muon channel, >=2J", filename="fastSimValid_jet1_bDiscrCSVMVA.png", weight=defaultWeight, normalization="unity")

#|eta_lj| in 2J1T
plotComp("abs(_lowestBTagJet_0_Eta)", [20, 0, 5], baseCut+leptonCut+Cuts.jets_2J1T, varName="|#eta|_{lj}", title=" in muon channel, 2J1T", filename="fastSimValid_etalj_2J1T.png", weight=defaultWeight, normalization="unity")

#Mtop, 2j1t, 2j0t, 3j1t, 3j2t

#Jet bDisriminator TCHP in mu & >=2J
cuts = {
    "2J0T": Cuts.jets_2J0T,
    "2J1T": Cuts.jets_2J1T,
    "3J1T": Cuts.jets_3J1T,
    "3J1T": Cuts.jets_3J2T,
}
for (cutn, cut) in cuts.items():
    plotComp("_recoTop_0_Mass", [20, 100, 400], baseCut+leptonCut+cut, varName="m_{bl#nu}", title=" in muon channel, {0}".format(cutn), filename="fastSimValid_mlnu_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")
    plotComp("cosThetaLightJet_cosTheta", [20, -1, 1], baseCut+leptonCut+cut, varName="cos #theta^{*}", title=" in muon channel, {0}".format(cutn), filename="fastSimValid_cosTheta_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")


