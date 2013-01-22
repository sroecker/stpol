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
      "13JulReReco": Lumi("13JulReReco",
        "/Reprocessing/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt")
    , "24AugReReco": Lumi("24AugReReco",
        "/Reprocessing/Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt")
    , "06AugReReco": Lumi("06AugReReco",
        "/Reprocessing/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt")
    , "PromptReco": Lumi("PromptReco",
        "/Prompt/Cert_190456-207898_8TeV_PromptReco_Collisions12_JSON.txt")
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
    def __init__(self, name, ds, lumi, globalTag, runrange):
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

#Datasets and run ranges come from:
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/PdmV2012Analysis#Analysis_based_on_CMSSW_5_3_X_re
#The global tags come from:
#https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuideFrontierConditions?redirectedfrom=CMS.SWGuideFrontierConditions
step1_data = [
      DS_Data("SingleMu_RunA",
      "/SingleMu/Run2012A-13Jul2012-v1/AOD", "13JulReReco", "FT_53_V6_AN3", [190456,193621])
      
    , DS_Data("SingleElectron_Run2012A_06AugReReco",
      "/SingleElectron/Run2012A-recover-06Aug2012-v1/AOD", "06AugReReco", "FT_53_V6C_AN3", [190782, 190949])      
      
    , DS_Data("SingleMu_Run2012B",
      "/SingleMu/Run2012B-13Jul2012-v1/AOD", "13JulReReco", "FT_53_V6_AN3", [193833, 196531])
      
    , DS_Data("SingleElectron_Run2012C_24AugReReco",
      "/SingleElectron/Run2012C-24Aug2012-v1/AOD", "24AugReReco", "FT_53_V10_AN3", [198022, 198913])      
      
    , DS_Data("SingleMu_Run2012C_v1",
      "/SingleMu/Run2012C-PromptReco-v1/AOD", "PromptReco", "FT_P_V42C_AN3", [-1, -1])
      
    , DS_Data("SingleMu_Run2012C_v2",
      "/SingleMu/Run2012C-PromptReco-v2/AOD", "PromptReco", "FT_P_V42C_AN3", [198934, 203746])
      

    , DS_Data("SingleElectron_Run2012A",
      "/SingleElectron/Run2012A-13Jul2012-v1/AOD", "13JulReReco", "FT_53_V6_AN3", [-1, -1])
      
    , DS_Data("SingleElectron_Run2012B",
      "/SingleElectron/Run2012B-13Jul2012-v1/AOD", "13JulReReco", "FT_53_V6_AN3", [-1, -1])
      
    , DS_Data("SingleElectron_Run2012C_v1",
      "/SingleElectron/Run2012C-PromptReco-v1/AOD", "PromptReco", "FT_P_V42C_AN3", [-1, -1])
      
    , DS_Data("SingleElectron_Run2012C_v2",
      "/SingleElectron/Run2012C-PromptReco-v2/AOD", "PromptReco", "FT_P_V42C_AN3", [-1, -1]ls
      )

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
    #/TTJets_SemiLeptMGDecays_8TeV-madgraph
    #/TTJets_FullLeptMGDecays_8TeV-madgraph
    #/TbarToLeptons_t-channel_TuneZ2star_8TeV-powheg-tauola
    #/TToLeptons_t-channel_TuneZ2star_8TeV-powheg-tauola
    #, DS("TTbarSemiLeptonic", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    #, DS("TTbar", "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM")
    
]

"""
Possible dataset sets to process
"""
possible_ds = {
    "S1D": step1_data,
    "S1MC": step1_MC
    }

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

