from anfw import *

enabledSamplesMC = {
    "T_t": "WD_T_t.root",
    "Tbar_t": "WD_Tbar_t.root",
    "T_tW": "WD_T_tW.root",
    "Tbar_tW": "WD_Tbar_tW.root",
    "T_s": "WD_T_s.root",
    "Tbar_s": "WD_Tbar_s.root",
    
#    "DYJets": "WD_DYJets.root",
    "WW": "WD_WW.root",
    "WZ": "WD_WZ.root",
    #"ZZ": "WD_ZZ.root",
    
    "WJets": "WD_WJets1.root",
    "TTbar": "WD_TTBar.root",
    
    "QCDMu": "WD_QCDMu.root",
    "QCD_Pt_20_30_BCtoE": "WD_QCD_Pt_20_30_BCtoE.root",
    "QCD_Pt_30_80_BCtoE": "WD_QCD_Pt_30_80_BCtoE.root",
    "QCD_Pt_80_170_BCtoE": "WD_QCD_Pt_80_170_BCtoE.root",
    "QCD_Pt_170_250_BCtoE": "WD_QCD_Pt_170_250_BCtoE.root",
    "QCD_Pt_250_350_BCtoE":"WD_QCD_Pt_250_350_BCtoE.root",
    "QCD_Pt_350_BCtoE": "WD_QCD_Pt_350_BCtoE.root",

    "QCD_Pt_20_30_EMEnriched": "WD_QCD_Pt_20_30_EMEnriched.root",
    "QCD_Pt_30_80_EMEnriched": "WD_QCD_Pt_30_80_EMEnriched.root",
    "QCD_Pt_80_170_EMEnriched": "WD_QCD_Pt_80_170_EMEnriched.root",
    "QCD_Pt_170_250_EMEnriched": "WD_QCD_Pt_170_250_EMEnriched.root",
    "QCD_Pt_250_350_EMEnriched": "WD_QCD_Pt_250_350_EMEnriched.root",
    "QCD_Pt_350_EMEnriched": "WD_QCD_Pt_350_EMEnriched.root",
}
enabledSamplesData = {
    "SingleEle": "SingleEle_merged_4729_pb.root",
    "SingleMu": "SingleMu_merged_8190_pb.root",
}

samplesMC = loadSamples(enabledSamplesMC)
samplesData = loadSamples(enabledSamplesData)

lumiMu = samplesData["SingleMu"].lumi
lumiEle = samplesData["SingleEle"].lumi

def plotVar(var, r, cut, integratedDataLumi):

    hists = dict()
    for (sampleName, sample) in samplesMC.items():
        hists[sampleName] = sample.plot1D(var, r, cut=cut, integratedDataLumi=integratedDataLumi)
    for (sampleName, sample) in samplesData.items():
        hists[sampleName] = sample.plot1D(var, r, cut=cut, weight=1.0, integratedDataLumi=1.0)

    merge = [
        ["tW", ".+_tW$"],
        ["s", ".+_s$"],
        ["t#bar{t}", "TTbar$"],
        ["data", "^Single(Mu|Ele)"],
        ["WJets", "WJets$"],
        ["QCD", "QCD.+"],
        ["diboson", "WW|WZ|ZZ"],
        ["t", ".+_t$"],
    ]

    merged = mergeHists(hists, merge)
    mergedData = merged.pop("data")
    mergedBG = merged

    c = ROOT.TCanvas()
    leg = legend("R")
    stack = ROOT.THStack()
    for (name, hist) in mergedBG.items():
        leg.AddEntry(hist, name)
        stack.Add(hist)
    stack.Draw("HIST F")
    mergedData.Draw("E1 SAME")
    leg.Draw()
    return c, leg, hists, mergedData

c1, leg1, h1, mergedData = plotVar("cosThetaLightJet_cosTheta", [20, -1, 1], Cuts.mu, lumiMu)
#c1.Print("plots/cosTheta_finalMu.png")
#c2, leg2, h2 = plotVar("cosThetaLightJet_cosTheta", [20, -1, 1], Cuts.finalEle, lumiEle)
#c2.Print("plots/cosTheta_finalEle.png")


