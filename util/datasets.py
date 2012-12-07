import sys
import os

import argparse
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument("-t", "--tag", type=str, default="notag",
                    help="A unique tag for this processing")
parser.add_argument("-s1d", "--step1Data", action="store_true", default=False,
                    help="Prepare the files for step1 data")
parser.add_argument("-T", "--template", type=str, default="", required=True,
                    help="template file to use")
args = parser.parse_args()
print args

lumis = {
    "13JulReReco": "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_190456-196531_8TeV_13Jul2012ReReco_Collisions12_JSON_v2.txt"
    , "24AugReReco": "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_198022-198523_8TeV_24Aug2012ReReco_Collisions12_JSON.txt"
    , "06AugReReco": "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Reprocessing/Cert_190782-190949_8TeV_06Aug2012ReReco_Collisions12_JSON.txt"
    , "PromptReco": "https://cms-service-dqm.web.cern.ch/cms-service-dqm/CAF/certification/Collisions12/8TeV/Prompt/Cert_190456-207898_8TeV_PromptReco_Collisions12_JSON.txt"
}

class Data:
    def __init__(self, ds, lumi):
        self.ds = ds
        self.lumi = lumi

step1_data = {
      "SingleMu_Run2012A": Data("/SingleMu/Run2012A-13Jul2012-v1/AOD", "13JulReReco")
    , "SingleMu_Run2012B": Data("/SingleMu/Run2012B-13Jul2012-v1/AOD", "13JulReReco")
    , "SingleMu_Run2012C_v1": Data("/SingleMu/Run2012C-PromptReco-v1/AOD", "PromptReco")
    , "SingleMu_Run2012C_v2": Data("/SingleMu/Run2012C-PromptReco-v2/AOD", "PromptReco")

    , "SingleElectron_Run2012A": Data("/SingleElectron/Run2012A-13Jul2012-v1/AOD", "13JulReReco")
    , "SingleElectron_Run2012B": Data("/SingleElectron/Run2012B-13Jul2012-v1/AOD", "13JulReReco")
    , "SingleElectron_Run2012C_24AugReReco": Data("/SingleElectron/Run2012C-24Aug2012-v1/AOD", "24AugReReco")
    , "SingleElectron_Run2012C_v1": Data("/SingleElectron/Run2012C-PromptReco-v1/AOD", "PromptReco")
    , "SingleElectron_Run2012C_v2": Data("/SingleElectron/Run2012C-PromptReco-v2/AOD", "PromptReco")
    , "SingleElectron_Run2012A_06AugReReco": Data("/SingleElectron/Run2012A-recover-06Aug2012-v1/AOD", "06AugReReco")

}

step1_MC = {
    "T_t":          "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_t":       "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "T_s":          "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_s":       "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "T_tW":         "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_tW":      "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "TTbar":        "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

#    "WJets1":       "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM", #smaller WJets sample
    "WJets2":       "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM", #larger WJets sample

    "WW":           "/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "WZ":           "/WZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "ZZ":           "/ZZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "GJets1":       "/GJets_HT-200To400_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "GJets2":       "/GJets_HT-400ToInf_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "QCD_Mu":       "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "QCD_BCtoE1":   "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE2":   "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE3":   "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE4":   "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE5":   "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE5":   "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_BCtoE6":   "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",

    "QCD_EM1":      "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_EM2":      "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_EM3":      "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_EM4":      "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_EM5":      "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "QCD_EM6":      "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "DYJets":       "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
}

# /QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER

# /QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER
# /QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER

step2_DS = {
    "T_t":          "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    "Tbar_t":       "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    "T_s":          "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    "Tbar_s":       "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    "T_tW":         "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    "Tbar_tW":      "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    "TTbar":        "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    "WJets":       "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    "WW":           "/WW_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    "WZ":           "/WZ_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    "ZZ":           "/ZZ_TuneZ2star_8TeV_pythia6_tauola/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    # "GJets1":       "/GJets_HT-200To400_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "GJets2":       "/GJets_HT-400ToInf_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "QCD_Mu":       "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",

    # "QCD_BCtoE1":   "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    # "QCD_BCtoE2":   "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
    # "QCD_BCtoE3":   "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_BCtoE4":   "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_BCtoE5":   "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_BCtoE5":   "/QCD_Pt_250_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_BCtoE6":   "/QCD_Pt_350_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",

    # "QCD_EM1":      "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_EM2":      "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_EM3":      "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_EM4":      "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_EM5":      "/QCD_Pt_250_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    # "QCD_EM6":      "/QCD_Pt_350_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "DYJets":       "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/jpata-stpol_v3_1-33f82354a36574c1158b3181d92c6119/USER",
}

def read_template(fn):
    f = open(fn)
    s = f.read()
    f.close()
    return s

tag = args.tag
template = read_template(args.template)
doData = args.step1Data


def parse_data_template(name, tag, dataset, lumi, ofdir):
    ofile = ofdir + "/" + "crab_%s_%s.cfg" % (name, tag)
    workdir = "WD_%s_%s" % (name, tag)
    out = template
    out = out.replace("DATASET", dataset)
    out = out.replace("WORKDIR", workdir)
    out = out.replace("TAG", tag)
    lumifile = lumis[lumi]
    lumifile = lumifile[lumifile.rindex("/")+1:]
    out = out.replace("LUMIFILE", lumifile)
    f = open(ofile, "w")
    f.write(out)
    f.close()
    print "Wrote %s" % ofile

if doData:
    #Prepare output directory
    ofdir = "crabs_%s" % tag
    ofdir_data = ofdir + "/data"
    ofdir_mc = ofdir + "/mc"
    os.mkdir(ofdir)
    os.mkdir(ofdir_data)
    os.mkdir(ofdir_mc)
    for (name, dataset) in step1_data.items():
        parse_data_template(name, tag, dataset.ds, dataset.lumi, ofdir_data)

#fname = sys.argv[1]
#print "Opening template %s" % fname
#f = open(fname)
#if len(sys.argv)>2:
#    tag = sys.argv[2]
#else:
#    tag = "NOTAG"
#
#template = f.read()
#f.close()
#
#ofdir = "crabs_%s" % tag
#os.mkdir(ofdir)
#
#ds = step2_DS
#
#for (k, v) in ds.items():
#    print k
#    temp = template
#    if "DATASET" in temp:
#        temp = temp.replace("DATASET", ds[k])
#    if "WORKDIR" in template:
#        temp = temp.replace("WORKDIR", "WD_%s" % k)
#    if "TAG" in temp:
#        temp = temp.replace("TAG", tag)
#    f = open("%s/crab_%s.cfg" % (ofdir, k), "w")
#    f.write(temp)
#    f.close()

