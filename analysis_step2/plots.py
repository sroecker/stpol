from anfw import *

enabledSamples = {
    "SingleEle": "SingleEle_merged_4729_pb.root",
    "SingleMu": "SingleMu_merged_8190_pb.root",
    
    "T_t": "WD_T_t.root",
    "Tbar_t": "WD_Tbar_t.root",
    "T_tW": "WD_T_tW.root",
    "Tbar_tW": "WD_Tbar_tW.root",
    "T_s": "WD_T_s.root",
    "Tbar_s": "WD_Tbar_s.root",
    
    "DYJets": "WD_DYJets.root",
    "WW": "WD_WW.root",
    "WZ": "WD_WZ.root",
    "ZZ": "WD_ZZ.root",
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
samples = loadSamples(enabledSamples)

lumiMu = samples["SingleMu"].lumi
lumiEle = samples["SingleEle"].lumi

h1 = samples["T_t"].plot1D("_goodSignalElectrons_0_mvaID", [20, 0, 1], integratedDataLumi=lumiEle)
h2 = samples["Tbar_t"].plot1D("_goodSignalElectrons_0_mvaID", [20, 0, 1], integratedDataLumi=lumiEle)
h2 = samples["QCDMu"].plot1D("_goodSignalElectrons_0_mvaID", [20, 0, 1], integratedDataLumi=lumiEle)