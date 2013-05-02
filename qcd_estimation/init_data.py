from Dataset import *
from DatasetGroup import *
from ROOT import *
from copy import copy, deepcopy
#from plot_settings import *

#input_path = "/hdfs/local/stpol/5_3/trees_fullIso/"
#input_path = "/hdfs/local/stpol/5_3/trees_fullIso_Mu/"
#input_path = "/hdfs/local/stpol/5_3/trees_2J0T/"
#/hdfs/local/stpol/5_3/trees_fullIso_MuTrigger/
#input_path = "~joosep/singletop/data/trees/Feb24/"
input_path = "~andres/single_top/stpol/out_step3/31042013/"
input_path_antiIso = input_path + "antiiso"
input_path_Iso = input_path + "iso"

groups = []
MCgroups = []
MC_groups_noQCD = []

group_IsoUp = []
group_IsoDown = []

dgDibosons = DatasetGroup("Dibosons", kBlue)
dWW = Dataset("WW", "WW", "WW", 54.838)
dWZ = Dataset("WZ", "WZ", "WZ", 33.2161)
dZZ = Dataset("ZZ", "ZZ", "ZZ", 8.25561)
dgDibosons.add([dWW,dWZ,dZZ])

dgQCD = DatasetGroup("QCD", kGray)
dQCDMu = Dataset("QCDMu", "QCDMu", "QCDMu", 134680.)
dQCDEM1 = Dataset("QCD_Pt-20to30_EMEnriched", "QCD_Pt_20to30_EMEnriched", input_path+"trees_QCD_Pt-20to30_EMEnriched.root")
dQCDEM2 = Dataset("QCD_Pt-30to80_EMEnriched", "QCD_Pt_30to80_EMEnriched", input_path+"trees_QCD_Pt-30to80_EMEnriched.root")
dQCDEM3 = Dataset("QCD_Pt-80to170_EMEnriched", "QCD_Pt_80to170_EMEnriched", input_path+"trees_QCD_Pt-80to170_EMEnriched.root")
dQCDBC1 = Dataset("QCD_Pt-20to30_BCtoE", "QCD_Pt_20to30_BCtoE", input_path+"trees_QCD_Pt-20to30_BCtoE.root")
dQCDBC2 = Dataset("QCD_Pt-30to80_BCtoE", "QCD_Pt_30to80_BCtoE", input_path+"trees_QCD_Pt-30to80_BCtoE.root")
dQCDBC3 = Dataset("QCD_Pt-80to170_BCtoE", "QCD_Pt_80to170_BCtoE", input_path+"trees_QCD_Pt-80to170_BCtoE.root")
#dgQCD.add([dQCDMu, dQCDEM1, dQCDEM2, dQCDEM3, dQCDBC1, dQCDBC2, dQCDBC3])
dgQCD.add(dQCDMu)


dgQCD_Mu = DatasetGroup("QCD", kGray, True, 2, "MC, Mu trigger")
dQCDMu_Mu = Dataset("QCDMu_Mu", "QCDMu_Mu", "/hdfs/local/stpol/5_3/trees_fullIso_Mu/"+"QCDMu.root", 134680.)
#dgQCD.add([dQCDMu, dQCDEM1, dQCDEM2, dQCDEM3, dQCDBC1, dQCDBC2, dQCDBC3])
dgQCD_Mu.add(dQCDMu_Mu)

"""
dgGJets = DatasetGroup("GJets", kCyan)
dGJHT40 = Dataset("GJets_HT-40To100", "HT_40To100", input_path+"trees_GJets_HT-40To100.root")
dGJHT100 = Dataset("GJets_HT-100To200", "HT_100To200", input_path+"trees_GJets_HT-100To200.root")
dGJHT200 = Dataset("GJets_HT-200", "HT_200", input_path+"trees_GJets_HT-200.root")
dgGJets.add([dGJHT40, dGJHT100, dGJHT200])
"""
dgTCh = DatasetGroup("t-channel", kRed)
dTCh = Dataset("t-channel", "TChannel", "T_t", 56.4)
#dTCh2 = Dataset("t-channel2", "TChannel", "T_t_toLeptons", 56.4)
dTbarCh = Dataset("t-channel_Tbar", "TbarChannel", "Tbar_t", 30.7)
#dTbarCh2 = Dataset("t-channel_Tbar2", "TbarChannel", "Tbar_t_toLeptons", 30.7)
dgTCh.add([dTCh, dTbarCh])

dgTWCh = DatasetGroup("tW-channel", kOrange)
dTWCh = Dataset("tW-channel", "TWChannel", "T_tW", 11.1)
dTbarWCh = Dataset("tW-channel_Tbar", "TbarWChannel", "Tbar_tW", 11.1)
dgTWCh.add([dTWCh, dTbarWCh])

dgSCh = DatasetGroup("s-channel", kYellow )
dSCh = Dataset("s-channel", "SChannel", "T_s", 3.79)
dSbarCh = Dataset("s-channel_Tbar", "SbarChannel", "Tbar_s", 1.76)
dgSCh.add([dSCh,dSbarCh])

dgTTBar = DatasetGroup("t #bar{t}", kOrange-3)
dTTBar = Dataset("TTJets", "TTBar", "TTJets_MassiveBinDECAY", 234.)
dTTBar2 = Dataset("TTJets2", "TTBar", "TTJets_FullLept", (0.326**2) * 234, 4246444 + 12119013)
dTTBar3 = Dataset("TTJets3", "TTBar", "TTJets_SemiLept", (0.676*0.326*2) * 234, 11229902 + 25424818)
#dgTTBar.add([dTTBar])
dgTTBar.add([dTTBar2, dTTBar3])

WJets_lo_nnlo_scale_factor = 37509/30400.0
dgWJets = DatasetGroup("W+Jets", kGreen+4)
#dWJets = Dataset("WJets", "WJets", "WJets_inclusive", 37509)
dW1Jets = Dataset("W+1Jets", "W+1Jets", "W1Jets_exclusive", 5400.0 * WJets_lo_nnlo_scale_factor)
dW2Jets = Dataset("W+2Jets", "W+2Jets", "W2Jets_exclusive", 1750.0 * WJets_lo_nnlo_scale_factor)
dW3Jets = Dataset("W+3Jets", "W+3Jets", "W3Jets_exclusive", 519.0 * WJets_lo_nnlo_scale_factor)
dW4Jets = Dataset("W+4Jets", "W+4Jets", "W4Jets_exclusive", 214.0 * WJets_lo_nnlo_scale_factor)
#dgWJets.add([dWJets])
dgWJets.add([dW1Jets, dW2Jets, dW3Jets, dW4Jets])



dgZJets = DatasetGroup("Z+Jets", kBlue-1)
dZJets = Dataset("DYJets", "ZJets", "DYJets", 3503.71)
dgZJets.add(dZJets)

dgData = DatasetGroup("Data", kBlack, False)
dSingleMuAB = Dataset("dataMuAB", "Data", "SingleMuAB", MC=False,lepton_type="mu")
dSingleMuC = Dataset("dataMuC", "Data", "SingleMuC", MC=False,lepton_type="mu")
dSingleMuD = Dataset("dataMuD", "Data", "SingleMuD", MC=False,lepton_type="mu")
#dSingleMuA = Dataset("dataMu", "Data", input_path+"SingleMuA.root", MC=False,lepton_type="mu",prescale = 90)
dgData.add([dSingleMuAB, dSingleMuC, dSingleMuD])


data_group = dgData

MC_groups_noQCD.append(dgTCh)
MC_groups_noQCD.append(dgTWCh)
MC_groups_noQCD.append(dgSCh)
MC_groups_noQCD.append(dgTTBar)
MC_groups_noQCD.append(dgWJets)
MC_groups_noQCD.append(dgZJets)
MC_groups_noQCD.append(dgDibosons)

mc_groups = copy(MC_groups_noQCD)
mc_groups.append(dgQCD)

lumiABIso = 5140.
lumiCIso = 6451.
lumiDIso = 6471.

dataLumiIso = lumiABIso + lumiCIso + lumiDIso

lumiABAntiIso = 5140.
lumiCAntiIso = 6451.
lumiDAntiIso = 6471.

dataLumiAntiIso = lumiABAntiIso + lumiCAntiIso + lumiDAntiIso
