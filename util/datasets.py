#!/usr/bin/python2.7
"""
This file collects the various datasets used for the stpol analysis and creates
crab.cfg files from these datasets based on a template.
Author: Joosep Pata joosep.pata@cern.ch
"""

import sys
import os
import argparse

"""
Represents a lumi file.
"""
class Lumi:
    lumiBase8TeV = "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/"

    def __init__(self, name, url, base=lumiBase8TeV):
        self.name = name
        self.url = base + url
        self.fname = url[url.rindex("/")+1:]

lumis = {

    "Run2012A-13Jul2012": Lumi("Run2012A-13Jul2012",
    "/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt")

    , "Run2012A-recover-06Aug2012": Lumi("Run2012A-recover-06Aug2012",
    "/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt")

    , "Run2012B-13Jul2012": Lumi("Run2012B-13Jul2012",
    "/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt")

    , "Run2012C-24Aug": Lumi("Run2012C-24Aug",
    "/Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt")

    , "Run2012C-PromptReco-v2": Lumi("Run2012C-PromptReco-v2",
    "/Cert_190456-203002_8TeV_PromptReco_Collisions12_JSON_v2.txt")

    , "Run2012C-EcalRecover_11Dec2012": Lumi("Run2012C-EcalRecover_11Dec2012",
    "/Cert_201191-201191_8TeV_11Dec2012ReReco-recover_Collisions12_JSON.txt")

    , "Run2012D-PromptReco-v1": Lumi("Run2012D-PromptReco-v1",
    "/Cert_190456-208686_8TeV_PromptReco_Collisions12_JSON.txt")

    , "total": Lumi("total",
    "/total.json")
}


"""
Represents a generic datasets.
"""
class DS:
    def __init__(self, name, ds):
        self.name = name
        self.ds = ds

    def parseTemplate(self, template, tag):
        out = template
        workdir = "WD_{0}".format(self.name)
        out = out.replace("TAG", tag)
        out = out.replace("DATASET", self.ds)
        out = out.replace("WORKDIR", workdir)
        return out

"""
Represents a Real Data dataset
"""
class DS_Data(DS):
    def __init__(self, name, ds, lumi, globalTag, runrange=None):
        DS.__init__(self, name, ds)
        self.lumi = lumi
        self.globalTag = globalTag
        self.runrange = runrange

    #FIXME: how to take into account the run range in the crab cfg?
    def parseTemplate(self, template, tag):
        out = template
        out = out.replace("LUMIFILE", lumis[self.lumi].fname)
        out = out.replace("GLOBALTAG", self.globalTag)
        out = DS.parseTemplate(self, out, tag)
        return out

    def __str__(self):
        return "{0} {1} {2} {3}".format(self.name, self.ds, self.lumi, self.globalTag)

"""
Represents a step2 MC dataset
"""
class DS_S2MC(DS):
    def __init__(self, name, ds, subchannel=None):
        self.name = name
        self.ds = ds
        if subchannel is None:
            subchannel = name
        self.subchannel = subchannel
        if subchannel == "T_t" or subchannel == "Tbar_T":
            self.channel = "signal"
        else:
            self.channel = "background"

    def parseTemplate(self, template, tag):
        out = template
        out = out.replace("SUBCHAN", self.subchannel)
        out = out.replace("CHANNEL", self.channel)

        out = DS.parseTemplate(self, out, tag)
        return out

#Top samples are in https://twiki.cern.ch/twiki/bin/view/CMS/TopSamplesSummer12#Prioritisation_for_Moriond2013

#Datasets and run ranges come from:
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2012Analysis#Analysis_based_on_CMSSW_5_3_X_re
#The global tags come from:
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions
step1_data = [

      DS_Data("SingleMu_Run2012A_13Jul2012_v1",
      "/SingleMu/Run2012A-13Jul2012-v1/AOD", "Run2012A-13Jul2012", "FT_53_V6_AN3::All", [190456,193621])

    , DS_Data("SingleMu_Run2012A_recover_06Aug2012_v1",
      "/SingleMu/Run2012A-recover-06Aug2012-v1/AOD", "Run2012A-recover-06Aug2012", "FT_53_V6_AN3::All", [193833, 196531])

    , DS_Data("SingleMu_Run2012B",
      "/SingleMu/Run2012B-13Jul2012-v1/AOD", "Run2012B-13Jul2012", "FT_53_V6_AN3::All", [193833, 196531])

      #RunC
#    , DS_Data("SingleMu_Run2012C_v1",
#      "/SingleMu/Run2012C-PromptReco-v1/AOD", "PromptReco", "FT_P_V42C_AN3::All", [-1, -1])

    , DS_Data("SingleMu_Run2012C-24Aug2012-v1",
      "/SingleMu/Run2012C-24Aug2012-v1/AOD", "Run2012C-24Aug", "FT_P_V42C_AN3::All", [198934, 203746])

    , DS_Data("SingleMu_Run2012C_v2",
      "/SingleMu/Run2012C-PromptReco-v2/AOD", "Run2012C-PromptReco-v2", "FT_P_V42C_AN3::All", [198934, 203746])

    , DS_Data("SingleMu_Run2012C-EcalRecover_11Dec2012",
      "/SingleMu/Run2012C-EcalRecover_11Dec2012-v1/AOD", "Run2012C-EcalRecover_11Dec2012", "FT_P_V42C_AN3::All", [201191, 201191])

      #RunD
    , DS_Data("SingleMu_Run2012D-PromptReco-v1",
      "/SingleMu/Run2012D-PromptReco-v1/AOD", "Run2012D-PromptReco-v1", "FT_P_V42_AN3::All", [203768, 208686])

##########
      #Electron
    , DS_Data("SingleElectron_Run2012A",
      "/SingleElectron/Run2012A-13Jul2012-v1/AOD", "Run2012A-13Jul2012", "FT_53_V6_AN3::All", [-1, -1])

    , DS_Data("SingleElectron_Run2012A_06AugReReco",
      "/SingleElectron/Run2012A-recover-06Aug2012-v1/AOD", "Run2012A-recover-06Aug2012", "FT_53_V6C_AN3::All", [190782, 190949])

    , DS_Data("SingleElectron_Run2012B",
      "/SingleElectron/Run2012B-13Jul2012-v1/AOD", "Run2012B-13Jul2012", "FT_53_V6_AN3::All", [-1, -1])

#    , DS_Data("SingleElectron_Run2012C_v1",
#      "/SingleElectron/Run2012C-PromptReco-v1/AOD", "PromptReco", "FT_P_V42C_AN3::All", [-1, -1])

    , DS_Data("SingleElectron_Run2012C_24AugReReco",
      "/SingleElectron/Run2012C-24Aug2012-v1/AOD", "Run2012C-24Aug", "FT_53_V10_AN3::All", [198022, 198913])

    , DS_Data("SingleElectron_Run2012C_v2",
      "/SingleElectron/Run2012C-PromptReco-v2/AOD", "Run2012C-PromptReco-v2", "FT_P_V42C_AN3::All", [-1, -1])

    , DS_Data("SingleElectron_Run2012C-EcalRecover_11Dec2012",
      "/SingleElectron/Run2012C-EcalRecover_11Dec2012-v1/AOD", "Run2012C-EcalRecover_11Dec2012", "FT_P_V42C_AN3::All", [201191, 201191])

    , DS_Data("SingleElectron_Run2012D-PromptReco-v1",
      "/SingleElectron/Run2012D-PromptReco-v1/AOD", "Run2012D-PromptReco-v1", "FT_P_V42_AN3::All", [-1, -1])
]

step2_newMC = [
    , DS_S2MC("Tbar_t_ToLeptons", "/TBarToLeptons_t-channel_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "Tbar_t")
    , DS_S2MC("T_t_ToLeptons", "/TToLeptons_t-channel_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "T_t")
    , DS_S2MC("WJets_inclusive", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "WJets")

    , DS_S2MC("W1Jets_exclusive", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "W1Jets")
    , DS_S2MC("W2Jets_exclusive", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "W2Jets")
    , DS_S2MC("W3Jets_exclusive", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "W3Jets")
    , DS_S2MC("W4Jets_exclusive", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "W4Jets")

    , DS_S2MC("DYJets", "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "DYJets")
    , DS_S2MC("QCDMu", "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCDMu")

    , DS_S2MC("QCD_Pt_20_30_BCtoE", "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_20_30_BCtoE")
    , DS_S2MC("QCD_Pt_20_30_EMEnriched", "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_20_30_EMEnriched")

    , DS_S2MC("QCD_Pt_30_80_BCtoE", "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_30_80_BCtoE")
    , DS_S2MC("QCD_Pt_30_80_EMEnriched", "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_30_80_EMEnriched")

    , DS_S2MC("QCD_Pt_80_170_BCtoE", "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_80_170_BCtoE")
    , DS_S2MC("QCD_Pt_80_170_EMEnriched", "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_80_170_EMEnriched")

    , DS_S2MC("QCD_Pt_170_250_BCtoE", "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_170_250_BCtoE")
    , DS_S2MC("QCD_Pt_170_250_EMEnriched", "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_170_250_EMEnriched")

    , DS_S2MC("QCD_Pt_250_350_BCtoE", "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_250_350_BCtoE")
    , DS_S2MC("QCD_Pt_250_350_EMEnriched", "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_250_350_EMEnriched")

    , DS_S2MC("QCD_Pt_350_BCtoE", "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_350_BCtoE")
    , DS_S2MC("QCD_Pt_350_EMEnriched", "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "QCD_Pt_350_EMEnriched")

    , DS_S2MC("GJets1", "/GJets_HT-200To400_8TeV-madgraph/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "GJets_HT-200To400")
    , DS_S2MC("GJets2", "/GJets_HT-400ToInf_8TeV-madgraph/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "GJets_HT-400ToInf")

    , DS_S2MC("Tbar_s", "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "Tbar_s")
    , DS_S2MC("Tbar_t", "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-e6b78fe04780b6676ee83481993719dd/USER", "Tbar_t")
    , DS_S2MC("Tbar_t_toLeptons", "/TBarToLeptons_t-channel_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "Tbar_t")
    , DS_S2MC("Tbar_tW", "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "Tbar_tW")
    , DS_S2MC("T_s", "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "T_s")
    , DS_S2MC("T_t", "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-e6b78fe04780b6676ee83481993719dd/USER", "T_t")
    , DS_S2MC("TTJets_FullLept", "/TTJets_FullLeptMGDecays_8TeV-madgraph/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "TTbar")
    , DS_S2MC("TTJets_MassiveBinDECAY", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "TTbar")
    , DS_S2MC("TTJets_SemiLept", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "TTbar")
    , DS_S2MC("T_tW", "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "T_tW")
    , DS_S2MC("W1Jets_exclusive", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "WJets")
    , DS_S2MC("W2Jets_exclusive", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "WJets")
    , DS_S2MC("W3Jets_exclusive", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "WJets")
    , DS_S2MC("W4Jets_exclusive", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER", "WJets")
    , DS_S2MC("WJets_inclusive", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "WJets")
    , DS_S2MC("WW", "/WW_TuneZ2star_8TeV_pythia6_tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "WW")
    , DS_S2MC("WZ", "/WZ_TuneZ2star_8TeV_pythia6_tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "WZ")
    , DS_S2MC("ZZ", "/ZZ_TuneZ2star_8TeV_pythia6_tauola/joosep-step1_MC_Feb6-243fe90abe1b1cf7bc2119dc7c0b2e28/USER", "ZZ")
]

step2_newData = [
    DS_Data("SingleMuC", "/SingleMu/joosep-step1_Data_Feb6-14d3879a0dccd7e6c1fb317f2674eaf1/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleMuAB", "/SingleMu/joosep-step1_Data_Feb6-2cdd420c4c725097a4330835f90d1ada/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleMuD", "/SingleMu/joosep-step1_Data_Feb6-4ad4eefaf926ac722f9a48104acbb5cc/USER", "total", "FT_53_V6_AN3::All"),

    DS_Data("SingleEleA1", "/SingleElectron/joosep-step1_Data_Feb6-a67a46c387bb052b77f0782979d2cf48/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleEleB", "/SingleElectron/joosep-step1_Data_Feb6-2cdd420c4c725097a4330835f90d1ada/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleEleC1", "/SingleElectron/joosep-step1_Data_Feb6-2d70b925c06acab65b2731ef9f08c3c1/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleEleC2", "/SingleElectron/joosep-step1_Data_Feb6-14d3879a0dccd7e6c1fb317f2674eaf1/USER", "total", "FT_53_V6_AN3::All"),
    DS_Data("SingleEleD", "/SingleElectron/joosep-step1_Data_Feb6-4ad4eefaf926ac722f9a48104acbb5cc/USER", "total", "FT_53_V6_AN3::All"),
]

step1_MC = [
      DS("T_t", "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("Tbar_t", "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("T_s", "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("Tbar_s", "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("T_tW", "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("Tbar_tW", "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("TTbar", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("WJets1", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM") #smaller WJets sample
    , DS("WJets2", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM") #larger WJets sample

    , DS("WW", "/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WZ", "/WZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("ZZ", "/ZZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("GJets1", "/GJets_HT-200To400_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("GJets2", "/GJets_HT-400ToInf_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("QCD_Mu", "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("QCD_BCtoE1", "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE2", "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE3", "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE4", "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE5", "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_BCtoE6", "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM")

    , DS("QCD_EM1", "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM2", "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM3", "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM4", "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM5", "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("QCD_EM6", "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    , DS("DYJets", "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    #From https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=228739
    , DS("TTbar_SemiLept1", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("TTbar_SemiLept2", "/TTJets_SemiLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A_ext-v1/AODSIM")
    , DS("TTbar_FullLept1", "/TTJets_FullLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("TTbar_FullLept2", "/TTJets_FullLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM")

    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FTToLeptons_t-channel_*AODSIM
    , DS("TToLeptons_t-channel", "/TToLeptons_t-channel_8TeV-powheg-tauola/Summer12-START52_V9_FSIM-v3/AODSIM")
    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FTbarToLeptons_t-channel*AODSIM
    , DS("TbarToLeptons_t-channel", "/TBarToLeptons_t-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")

    #https://cmsweb.cern.ch/das/request?view=list&limit=10&instance=cms_dbs_prod_global&input=dataset+dataset%3D%2FW*JetsToLNu_TuneZ2Star_8TeV-madgraph%2FSummer12_DR53X-PU_S10_START53*AODSIM
    , DS("WJets_excl1", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl2", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl3", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    , DS("WJets_excl4", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
]

step1_FSIM_Valid = [
    DS("TTJets_FSIM_Valid_FastSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12-START53_V7C_FSIM-v1/AODSIM"),
    DS("TTJets_FSIM_Valid_FullSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7C-v1/AODSIM"),
]

step2_MC = [
    DS_S2MC("T_t", "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "T_t"),
    DS_S2MC("Tbar_t", "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "Tbar_t"),

    DS_S2MC("T_s", "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "T_s"),
    DS_S2MC("Tbar_s", "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "Tbar_s"),

    DS_S2MC("T_tW", "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "T_tW"),
    DS_S2MC("Tbar_tW", "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "Tbar_tW"),

    DS_S2MC("WJets_inclusive", "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "WJets"),
    DS_S2MC("W1Jets_exclusive", "/W1JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER"),
    DS_S2MC("W2Jets_exclusive", "/W2JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER"),
    DS_S2MC("W3Jets_exclusive", "/W3JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER"),
    DS_S2MC("W4Jets_exclusive", "/W4JetsToLNu_TuneZ2Star_8TeV-madgraph/jpata-Jan31_WJets_samples-6154e41574fbefb9af6528e169eaecf5/USER"),

    DS_S2MC("TTbar", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "TTbar"),

    DS_S2MC("WW", "/WW_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "WW"),
    DS_S2MC("WZ", "/WZ_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "WZ"),
    DS_S2MC("ZZ", "/ZZ_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "ZZ"),

    DS_S2MC("DYJets", "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "DYJets"),

    DS_S2MC("QCDMu", "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER", "QCDMu"),

    DS_S2MC("QCD_Pt_20_30_EMEnriched", "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_30_80_EMEnriched", "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_80_170_EMEnriched", "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_170_250_EMEnriched", "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_250_350_EMEnriched", "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_350_EMEnriched", "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),

    DS_S2MC("QCD_Pt_20_30_BCtoE", "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_30_80_BCtoE", "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_80_170_BCtoE", "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_170_250_BCtoE", "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_250_350_BCtoE", "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),
    DS_S2MC("QCD_Pt_350_BCtoE", "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER"),

    DS_S2MC("TTJets_FSIM_Valid_FullSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation-243fe90abe1b1cf7bc2119dc7c0b2e28/USER#c66d2181-df08-407f-ae2e-0185b67e17cf"),

    DS_S2MC("TTJets_FSIM_Valid_FastSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation_v2_FSIM-243fe90abe1b1cf7bc2119dc7c0b2e28/USER"),


]

step2_FastSimValid = [
    DS_S2MC("TTJets_FSIM_Valid_FullSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation-243fe90abe1b1cf7bc2119dc7c0b2e28/USER#c66d2181-df08-407f-ae2e-0185b67e17cf"),

    DS_S2MC("TTJets_FSIM_Valid_FastSim", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_Feb8_FastSimValidation_v2_FSIM-243fe90abe1b1cf7bc2119dc7c0b2e28/USER")
]

#Jan31 partial reprocessing of step1
step2_data = [
    DS_Data("SingleMuAB", "/SingleMu/joosep-Jan31_all-ddb64625c246284e02e1dd440ed9dce0/USER", "total", "FT_53_V6_AN3::All")
    #, DS_Data("SingleMuB", "/SingleMu/joosep-Jan31_all-ddb64625c246284e02e1dd440ed9dce0/USER", "total", "FT_53_V6_AN3::All")
    , DS_Data("SingleMuC", "/SingleMu/joosep-Jan31_all-a2316588016b5c752b27be91245f9d8d/USER", "total", "FT_53_V6_AN3::All")

    , DS_Data("SingleEleA2", "/SingleElectron/joosep-Jan31_all-49eb03845dffa028caa53d26232b143a/USER", "total", "FT_53_V6_AN3::All")
    , DS_Data("SingleEleC", "/SingleElectron/joosep-Jan31_all-a2316588016b5c752b27be91245f9d8d/USER", "total", "FT_53_V6_AN3::All")
    , DS_Data("SingleEleA1", "/SingleElectron/joosep-Jan31_all-fd13d2df3af397f914d3b3a3be95a5ba/USER", "total", "FT_53_V6_AN3::All")
    , DS_Data("SingleEleD", "/SingleElectron/joosep-step1_Data_Feb5-1d982c38357b1be9f9666c2b21150ebd/USER", "total", "FT_53_V6_AN3::All")
]

"""
Possible dataset sets to process
"""
possible_ds = {
    "S1D": step1_data,
    "S1MC": step1_MC,
    "S2MC": step2_MC,
    "S2newMC": step2_newMC,
    "S2D": step2_data,
    "S2newD": step2_newData,
    "S2FSIM": step2_FastSimValid
    }

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Creates crab.cfg files based on \
                                                  a template file.')
    parser.add_argument("-t", "--tag", type=str, default="notag",
                        help="A unique tag for publishing")
    parser.add_argument("-T", "--template", type=str, default="", required=True,
                        help="template file to use")
    parser.add_argument("-o", "--ofdir", type=str, default="", required=True,
                        help="output directory for files")
    parser.add_argument("-d", "--data", type=str, default="", required=True,
                        help="name of the list of datasets to parse", choices=possible_ds.keys())
    args = parser.parse_args()
    print args
    tag = args.tag
    ofdir = args.ofdir

    def read_template(fn):
        f = open(fn)
        s = f.read()
        f.close()
        return s

    template = read_template(args.template)
    dslist = possible_ds[args.data]

    os.mkdir(ofdir)
    for ds in dslist:
        ofn = "{2}/crab_{0}_{1}.cfg".format(ds.name, tag, ofdir)
        of = open(ofn, "w")
        cfg = ds.parseTemplate(template, tag)
        of.write(cfg)
        of.close()
        print "{0} done".format(ofn)
