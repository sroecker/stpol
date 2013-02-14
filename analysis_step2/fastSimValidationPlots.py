from anfw import *
import pdb
import math
import re

lumi = 1000

logger = logging.getLogger("fastSimValidationPlots")

ROOT.gROOT.SetBatch(True)
samples = {
    "TTbar_fast": Channel(channelName="TTbar_fast", fileName=args.datadir + "/TTJets_FSIM_Valid_FastSim.root", crossSection=xs["TTbar"], color=ROOT.kRed),
    "TTbar_full": Channel(channelName="TTbar_full", fileName=args.datadir + "/TTJets_FSIM_Valid_FullSim.root", crossSection=xs["TTbar"], color=ROOT.kGreen),
}
ROOT.gROOT.cd()

def plotComp(var, r, cut, varName=None, title="", filename=None, weight=1.0, normalization="MC", dtype="float"):
    rs = randstr(4)

    if weight=="PUWeight_puWeightProducer":
        title += ", PU reweighted"

    if normalization=="lumi":
        def weightStr(x):
            return "%f*%s" % (x, weight)
        title += ", [events/fb/u]"

    elif normalization=="MC":
        def weightStr(x):
            return "%s" % weight
        title += ", [MC events/u]"

    elif normalization=="unity":
        def weightStr(x):
            return "%s" % weight
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
        chi2 = h_fast.Chi2Test(h_full, "WW CHI2/NDF")
        title += ", #chi^{2}/NDF=" + "{0:.1f}".format(chi2)
        logger.info("chi2h/ndf = {0}".format(chi2))
    h_fast.SetTitle(varName + title)

    c = ROOT.TCanvas(rs, rs)
    c.SetCanvasSize(1600,1024)
    c.SetRightMargin(0.3)

    h_fast.GetXaxis().SetTitle(varName)
    logger.debug("Drawing histogram {0}".format(h_fast))
    h_fast.Draw("H1")
    logger.debug("Drawing histogram {0}".format(h_full))
    h_full.Draw("H1 SAME")
    leg = legend("R")
    leg.SetTextFont(133)
    leg.SetTextSize(25)
    leg.SetFillStyle(4000)


    legEventsFull = ""
    legEventsFast = ""
    if normalization == "MC":
        legEventsFast = "{0:.2E} MC ev.".format(h_fast.Integral())
        legEventsFull = "{0:.2E} MC ev.".format(h_full.Integral())
    elif normalization == "lumi":
        legEventsFast = "{0:.1E} ev./fb".format(h_fast.Integral())
        legEventsFull = "{0:.1E} ev./fb".format(h_full.Integral())
    elif normalization == "unity":
        fastWeight = lumi*samples["TTbar_fast"].xsWeight
        fullWeight = lumi*samples["TTbar_full"].xsWeight
        fastCount = samples["TTbar_fast"].tree.GetEntries(cut.cutStr)
        fullCount = samples["TTbar_full"].tree.GetEntries(cut.cutStr)
        legEventsFast = "{0:.1f} #pm {1:.1f} ev./fb".format(fastWeight * fastCount, fastWeight * math.sqrt(fastCount))
        legEventsFull = "{0:.1f} #pm {1:.1f} ev./fb".format(fullWeight * fullCount, fullWeight * math.sqrt(fullCount))

    leg.AddEntry(h_fast, "#splitline{FastSim t#bar{t}}{%s}" % legEventsFast)
    leg.AddEntry(h_full, "#splitline{FullSim t#bar{t}}{%s}" % legEventsFull)
    leg.Draw()
    c.Show()
    if filename is not None:
        c.Print("plots/" + filename)
    return {"canvas": c, "h_fast": h_fast, "h_full": h_full, "leg": leg}

cutNVtxA = Cut("nVtx_0_15", "nVertices_puWeightProducer>=0 && nVertices_puWeightProducer< 15")
cutNVtxB = Cut("nVtx_15_30", "nVertices_puWeightProducer>=15 && nVertices_puWeightProducer< 30")
cutNVtxC = Cut("nVtx_30_50", "nVertices_puWeightProducer>=30 && nVertices_puWeightProducer< 50")
baseCut = Cuts.initial# + cutNVtxB
lepton="muon"
leptonCut = Cuts.mu
#defaultWeight = "1"
defaultWeight = "PUWeight_puWeightProducer"

#Vertices
nVertRange = [20, 0, 50]
prettyName = "N_{vtx.gen.}"
title = " after skim (muon+electron)"

plotComp("nVerticesTrue_puWeightProducer", nVertRange, baseCut, varName=prettyName, title=title, filename="fastSimValid_nVerts_unweighted.png")
plotComp("nVerticesTrue_puWeightProducer", nVertRange, baseCut, varName=prettyName, title=title, filename="fastSimValid_nVerts_weighted.png", weight=defaultWeight)
plotComp("_offlinePVCount", nVertRange, Cuts.initial, varName=prettyName, title=title, filename="fastSimValid_nVertsOffline_unweighted.png")
plotComp("_offlinePVCount", nVertRange, Cuts.initial, varName=prettyName, title=title, filename="fastSimValid_nVertsOffline_weighted.png", weight=defaultWeight)

#Leptons
filepref = "fastSimValid_%s_"%lepton
lepShort = {"muon":"muon", "electron":"ele"}
plotComp("_{0}sWithIso_0_Pt".format(lepShort[lepton]), [20, 0, 150], baseCut, varName="%s p_{T}"%lepton, title=" after skimming, before lepton ID", filename=filepref + "pt_weighted.png", weight=defaultWeight, normalization="unity")
plotComp("abs(_{0}sWithIso_0_Eta)".format(lepShort[lepton]), [20, 0, 2.6], baseCut, varName="%s |#eta|"%lepton, title=" after skimming, before lepton ID", filename=filepref + "eta_weighted.png", weight=defaultWeight, normalization="unity")

nbins=20
lepIDVars = {
    "muon":[
        ('_muonsWithIso_0_normChi2', (nbins, 0, 5))
        , ('_muonsWithIso_0_track_hitPattern_trackerLayersWithMeasurement', (20, 0, 20))
        , ('_muonsWithIso_0_globalTrack_hitPattern_numberOfValidMuonHits', (20, 0, 20))
        , ('_muonsWithIso_0_innerTrack_hitPattern_numberOfValidPixelHits', (10, 0, 10))
        , ('_muonsWithIso_0_db', (nbins, 0, 0.05))
        , ('_muonsWithIso_0_dz', (nbins, 0, 0.05))
        , ('_muonsWithIso_0_numberOfMatchedStations', (10, 0, 10))
    ],
    "electron":[
        ('_elesWithIso_0_mvaID', (20, 0, 1))
        , ('_elesWithIso_0_gsfTrack_trackerExpectedHitsInner_numberOfHits', (10, 0, 10))
    ]
}
lepPtEtaCuts = {
    "muon": Cut("muPtEta", "_muonsWithIso_0_Pt>26 && abs(_muonsWithIso_0_Eta)<2.1")
    , "electron": Cut("elePtEta", "_elesWithIso_0_Pt>30 && abs(_elesWithIso_0_Eta)<2.5")
}
for idvar, r in lepIDVars[lepton]:
    plotComp(idvar, r, baseCut + lepPtEtaCuts[lepton], varName=varNamePretty(idvar), title=" after skimming, lepton p_{T}, #eta cut", filename=filepref + idvar + "_weighted.png", weight=defaultWeight, normalization="unity")

#Reliso after ID
title = "in %s channel, lepton ID requirement, iso" % lepton
filepref="fastSimValid_%s_relIso" % lepton
lepIsoVars = {
    "muon": "_muonsWithIso_0_relIso"
    , "electron": "_elesWithIso_0_relIso"
}
plotComp(lepIsoVars[lepton], [20, 0, 0.15], baseCut+leptonCut, varName="N_{jets}", title=title, filename=filepref+".png", weight=defaultWeight, dtype="float", normalization="unity")

#Jet count in mu/ele
title=" in %s channel, after skim, ref. sel. lepton selection" % lepton
filepref="fastSimValid_nJets_%s" % lepton
plotComp("_bJetCount + _lightJetCount", [10, 0, 10], baseCut+leptonCut + Cut("jetOK", "_bJetCount>=0 && _lightJetCount>=0"), varName="N_{jets}", title=title, filename=filepref+".png", weight=defaultWeight, dtype="float", normalization="unity")

title=" in %s channel, after skim, ref. sel, lepton selection" % lepton
metVars = [
    #("_eleAndMETMT", "eleMT"),
    ("_muAndMETMT", "muMT"),
    ("_patMETs_0_Pt", "MET"),
]

for var, varName in metVars:
    plotComp(var, [20, 0, 200], baseCut+leptonCut, varName=varName, title=title, filename="fastSimValid_%s.png"%var, weight=defaultWeight, dtype="float", normalization="unity")

#Jet pt/eta in mu/ele
title=" in %s channel, after skim, ref. sel. lepton selection" % lepton
jetVars = [
      ("_goodJets_0_Pt", "leading jet p_{T}", "jet0pt", [20, 0, 300])
    , ("_goodJets_1_Pt", "second jet p_{T}", "jet1pt", [20, 0, 300])
    , ("abs(_goodJets_0_Eta)", "leading jet |#eta|", "jet0eta", [20, 0, 5])
    , ("abs(_goodJets_1_Eta)", "second jet |#eta|", "jet1eta", [20, 0, 5])
]
for var, varNamePr, varNameF, r in jetVars:
    plotComp(var, r, baseCut+leptonCut, varName=varNamePr, title=title, filename="fastSimValid_%s_%s.png"%(varNameF, lepton), weight=defaultWeight, normalization="unity")


#Jet bDisriminator TCHP in mu & >=2J
jetVars = [
      ("_goodJets_0_bDiscriminatorTCHP", "leading jet TCHP discr.", "jet0tchp", [20, -5, 10])
    , ("_goodJets_1_bDiscriminatorTCHP", "second jet TCHP discr.", "jet1tchp", [20, -5, 10])
    , ("_goodJets_0_bDiscriminatorCSV_MVA", "leading jet CSV-MVA discr.", "jet0csvmva", [20, 0, 1])
    , ("_goodJets_1_bDiscriminatorCSV_MVA", "second jet CSV-MVA discr.", "jet1csvmva", [20, 0, 1])
]
title=" in %s channel, after skim, ref. sel. lepton selection, >=2J" % lepton
for var, varName, varNameF, r in jetVars:
    plotComp(var, r, baseCut+leptonCut+Cuts.jets_2plusJ, varName=varName, title=title, filename="fastSimValid_%s.png"%varNameF, weight=defaultWeight, normalization="unity")

#|eta_lj| in 2J1T

title=" in %s channel, after skim, ref. sel. lepton selection, 2J1T" % lepton
plotComp("abs(_lowestBTagJet_0_Eta)",
    [20, 0, 5],
    baseCut+leptonCut+Cuts.jets_2J1T,
    varName="|%s|"%varNamePretty("_lowestBTagJet_0_Eta"),
    title=title,
    filename="fastSimValid_etalj_2J1T.png",
    weight=defaultWeight,
    normalization="unity")

#Mtop, cosTheta* in  2j1t, 2j0t, 3j1t, 3j2t
cuts = {
    "2J0T": Cuts.jets_2J0T,
    "2J1T": Cuts.jets_2J1T,
    "3J1T": Cuts.jets_3J1T,
    "3J1T": Cuts.jets_3J2T,
}
for (cutn, cut) in cuts.items():
    title = " in {1} channel, skim, ref. sel., {0}".format(cutn, lepton)
    plotComp("_recoTop_0_Mass", [20, 100, 400], baseCut+leptonCut+cut, varName="m_{bl#nu}", title=title, filename="fastSimValid_mlnu_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")
    plotComp("_recoTop_0_Pt", [20, 0, 400], baseCut+leptonCut+cut, varName="p_{T, top}", title=title, filename="fastSimValid_topPt_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")
    plotComp("abs(_recoTop_0_Eta)", [20, 0, 5], baseCut+leptonCut+cut, varName="|#eta|_{T, top}", title=title, filename="fastSimValid_topEta_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")
    plotComp("cosThetaLightJet_cosTheta", [20, -1, 1], baseCut+leptonCut+cut, varName="cos #theta *", title=title, filename="fastSimValid_cosTheta_{0}.png".format(cutn), weight=defaultWeight, normalization="unity")

vars3J1T = [
    ("_goodJets_0_Pt", "leading jet pt", [20, 0, 300], "jet0pt")
    , ("abs(_goodJets_0_Eta)", "leading jet eta", [20, 0, 5], "jet0eta")
    , ("cosThetaLightJet_cosTheta", "cos #theta *", [20, -1, 1], "costheta")
    , ("_goodSignalMuons_0_Pt", "muon pt", [20, 0, 300], "muPt")
    , ("_goodSignalElectrons_0_Pt", "electrons pt", [20, 0, 300], "elePt")
]

eta_low = 1.0
eta_high = 3.0
etaCut = Cut("midJetEta", "abs(_lowestBTagJet_0_Eta)>%f && abs(_lowestBTagJet_0_Eta<%f)" % (eta_low, eta_high))
for var, varName, r, varNameF in vars3J1T:
    plotComp(var,
        r,
        baseCut+leptonCut+Cuts.jets_3J1T+etaCut,
        varName=varName,
        title=" in %s channel, skim, ref.sel., 3J1T, %d < |#eta_{lj}| < %d"%(lepton, round(eta_low), round(eta_high)),
        filename="fastSimValid_3J1T_midEta_%s.png"%varNameF,
        weight=defaultWeight, normalization="unity"
    )

