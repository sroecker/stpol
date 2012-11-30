import sys
import os

step1_DS = {
    "T_t":          "/T_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_t":       "/Tbar_t-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "T_s":          "/T_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_s":       "/Tbar_s-channel_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "T_tW":         "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "Tbar_tW":      "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "TTbar":        "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",

    "WJets1":       "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM",
    "WJets2":       "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM",

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

step1_Data = {
    "SingleMu_RunA": "/SingleMu/Run2012A-13Jul2012-v1/AOD"
    "SingleMu_RunB": "/SingleMu/Run2012B-13Jul2012-v1/AOD",
    
}

fname = sys.argv[1]
print "Opening template %s" % fname
f = open(fname)
if len(sys.argv)>2:
    tag = sys.argv[2]
else:
    tag = "NOTAG"

template = f.read()
f.close()

ofdir = "crabs_%s" % tag
os.mkdir(ofdir)

ds = step2_DS

for (k, v) in ds.items():
    print k
    temp = template
    if "DATASET" in temp:
        temp = temp.replace("DATASET", ds[k])
    if "WORKDIR" in template:
        temp = temp.replace("WORKDIR", "WD_%s" % k)
    if "TAG" in temp:
        temp = temp.replace("TAG", tag)
    f = open("%s/crab_%s.cfg" % (ofdir, k), "w")
    f.write(temp)
    f.close()

