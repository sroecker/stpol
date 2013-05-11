#!/usr/bin/env cmsRun
import FWCore.ParameterSet.Config as cms
import os,sys,re,shutil


#Original config file
fileName = "TChannel_crab.cfg"
fileName2 = "SingleTopMC_TChannel_cfg.py"
#fileName = "SingleTopSystematics_cfg.py"
#fileName = "SingleTopSystematics_split_cfg.py"
#fileName = "SingleTopNEvents_cfg.py"

#Channels to include
channels = [
"TToBMuNu",
"TToBENu",
"TToBTauNu",
"TToBMuNu_0100",
"TToBENu_0100",
"TToBTauNu_0100",
"TToBMuNu_unphys",
"TToBENu_unphys",
"TToBTauNu_unphys",
#"QCD_Pt_20to30_EMEnriched",
#"QCD_Pt_30to80_EMEnriched",
#"QCD_Pt_80to170_EMEnriched",
#"QCD_Pt_170to250_EMEnriched",
#"QCD_Pt_20to30_BCtoE",
#"QCD_Pt_30to80_BCtoE",
#"QCD_Pt_80to170_BCtoE",
#"QCD_Pt_170to250_BCtoE",
#"QCD_HT_40_100_GJets",
#"QCD_HT_100_200_GJets",
#"QCD_HT_200_inf_GJets",
#"TChannel_Q2Up",
#"TChannel_Q2Down",
#"TbarChannel_Q2Up",
#"TbarChannel_Q2Down",
#"TTBar_Q2Up",
#"TTBar_Q2Down",
#"WJets_Q2Up",
#"WJets_Q2Down",
#"WJets_MatchingUp",
#"WJets_MatchingDown",
#"TTBar_MatchingUp",
#"TTBar_MatchingDown",
#"TTBar_MassUp",
#"TTBar_MassDown",
#"TChannel_MassUp",
#"TChannel_MassDown",
#"TbarChannel_MassUp",
#"TbarChannel_MassDown",
#"TbarWChannelFullLep_Q2Up",
#"TbarWChannelFullLep_Q2Down",
#"TWChannelFullLep_Q2Up",
#"TWChannelFullLep_Q2Down",#
#
#"TbarWChannelThadWlep_Q2Up",
#"TbarWChannelThadWlep_Q2Down",
#"TWChannelThadWlep_Q2Up",
#"TWChannelThadWlep_Q2Down",
#
#"TbarWChannelTlepWhad_Q2Up",
#"TbarWChannelTlepWhad_Q2Down",
#"TWChannelTlepWhad_Q2Up",
#"TWChannelTlepWhad_Q2Down",
#"TbarWChannelFullLep_MassUp",
#"TbarWChannelFullLep_MassDown",
#"TWChannelFullLep_MassUp",
#"TWChannelFullLep_MassDown",
#
#"TbarWChannelThadWlep_MassUp",
#"TbarWChannelThadWlep_MassDown",
#"TWChannelThadWlep_MassUp",
#"TWChannelThadWlep_MassDown",
#
#"TbarWChannelTlepWhad_MassUp",
#"TbarWChannelTlepWhad_MassDown",
#"TWChannelTlepWhad_MassUp",
#"TWChannelTlepWhad_MassDown",
#"WW",
#"WZ",
#"ZZ",
#"WJetsBig",
#"WJets",
#"TTBarFullLep",
#"TTBarSemiLep",
#"QCDMuBig",
#"QCDMu",
#"ZJets",
##"W1Jet",
##"W2Jets",
###"W3Jets",
####"W4Jets",
#"SbarChannel",
#"SChannel",
#"TbarChannel",
#"TWChannel",
#"TbarWChannel",
  ]


#Implementation:

def datasetmap(channel):
    if channel == "TChannel":
        return "/TToLeptons_t-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarChannel":
        return "/TBarToLeptons_t-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TToBMuNu":
        return "/TToBMuNu_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBENu":
        return "/TToBENu_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBTauNu":
        return "/TToBTauNu_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TToBMuNu_0100":
        return "/TToBMuNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBENu_0100":
        return "/TToBENu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBTauNu_0100":
        return "/TToBTauNu_anomWtb-0100_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TToBMuNu_unphys":
        return "/TToBMuNu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBENu_unphys":
        return "/TToBENu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TToBTauNu_unphys":
        return "/TToBTauNu_anomWtb-unphys_t-channel_TuneZ2star_8TeV-comphep/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"



    if channel == "SChannel":
        return "/TToLeptons_s-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "SbarChannel":
        return "/TBarToLeptons_s-channel_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TWChannel":
        return "/T_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannel":
        return "/Tbar_tW-channel-DR_TuneZ2star_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TTBarFullLep":
        return "/TTJets_FullLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TTBarSemiLep":
        return "/TTJets_SemiLeptMGDecays_8TeV-madgraph/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"


    if channel == "WJets":
        return "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "WJetsBig":
        return "/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM"

    if channel == "ZJets":
        return "/DYJetsToLL_M-50_TuneZ2Star_8TeV-madgraph-tarball/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "QCDMu":   
        return "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "QCDMuBig":   
        return "/QCD_Pt_20_MuEnrichedPt_15_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v3/AODSIM"

    if channel == "WW":
        return "/WW_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "WZ":
        return "/WZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
            
    if channel == "ZZ":
        return "/ZZ_TuneZ2star_8TeV_pythia6_tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"


#####SYSTEMATICS

    if channel == "TTBar_Q2Up":
        return "/TTJets_scaleup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TTBar_Q2Down":
        return "/TTJets_scaledown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TTBar_MassUp":
        return "/TTJets_mass178_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TTBar_MassDown":
        return "/TTJets_mass166_5_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TChannel_Q2Up":
        return "/TToLeptons_t-channel_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TChannel_Q2Down":
        return "/TToLeptons_t-channel_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TbarChannel_Q2Up":
        return "/TBarToLeptons_t-channel_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarChannel_Q2Down":
        return "/TBarToLeptons_t-channel_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TChannel_MassUp":
        return "/TToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TChannel_MassDown":
        return "/TToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "TbarChannel_MassUp":
        return "/TBarToLeptons_t-channel_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarChannel_MassDown":
        return "/TBarToLeptons_t-channel_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"


    if channel == "TWChannelFullLep_Q2Up":
        return "/TToDilepton_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelFullLep_Q2Down":
        return "/TToDilepton_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TbarWChannelFullLep_Q2Up":
        return "/TBarToDilepton_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelFullLep_Q2Down":
        return "/TBarToDilepton_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TWChannelThadWlep_Q2Up":
        return "/TToThadWlep_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelThadWlep_Q2Down":
        return "/TToThadWlep_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TbarWChannelThadWlep_Q2Up":
        return "/TBarToThadWlep_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelThadWlep_Q2Down":
        return "/TBarToThadWlep_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    

    if channel == "TWChannelTlepWhad_Q2Up":
        return "/TToTlepWhad_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelTlepWhad_Q2Down":
        return "/TToTlepWhad_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TbarWChannelTlepWhad_Q2Up":
        return "/TBarToTlepWhad_tW-channel-DR_scaleup_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelTlepWhad_Q2Down":
        return "/TBarToTlepWhad_tW-channel-DR_scaledown_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

#TW Mass

    if channel == "TWChannelFullLep_MassUp":
        return "/TToDilepton_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelFullLep_MassDown":
        return " /TToDilepton_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TbarWChannelFullLep_MassUp":
        return "/TBarToDilepton_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelFullLep_MassDown":
        return "/TBarToDilepton_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TWChannelThadWlep_MassUp":
        return "/TToThadWlep_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelThadWlep_MassDown":
        return "/TToThadWlep_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "TbarWChannelThadWlep_MassUp":
        return "/TBarToThadWlep_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelThadWlep_MassDown":
        return "/TBarToThadWlep_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"




    
    if channel == "TWChannelTlepWhad_MassUp":
        return "/TToTlepWhad_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TWChannelTlepWhad_MassDown":
        return "/TToTlepWhad_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
   
    if channel == "TbarWChannelTlepWhad_MassUp":
        return "/TBarToTlepWhad_tW-channel-DR_mass178_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TbarWChannelTlepWhad_MassDown":
        return "/TBarToTlepWhad_tW-channel-DR_mass166_5_8TeV-powheg-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    
#    

    if channel == "TTBar_MatchingDown":
        return "/TTJets_matchingdown_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "TTBar_MatchingUp":
        return "/TTJets_matchingup_TuneZ2star_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "WJets_Q2Up":
        return "/WJetsToLNu_scaleup_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v2/AODSIM"
    if channel == "WJets_Q2Down":
        return "/WJetsToLNu_scaledown_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    
    if channel == "WJets_MatchingUp":
        return "/WJetsToLNu_matchingup_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "WJets_MatchingDown":
        return "/WJetsToLNu_matchingdown_8TeV-madgraph-tauola/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

########END SYSTEMATICS

#Still TO BE UPDATED
    if channel == "TTBar":
        return "/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/Summer12-PU_S6_START52_V9-v1/AODSIM"


    if channel == "QCD_Pt_20to30_EMEnriched":
                return "/QCD_Pt_20_30_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_30to80_EMEnriched":
                return "/QCD_Pt_30_80_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_80to170_EMEnriched":
                return  "/QCD_Pt_80_170_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_170to250_EMEnriched":
                return  "/QCD_Pt_170_250_EMEnriched_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "QCD_Pt_20to30_BCtoE":
                return "/QCD_Pt_20_30_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_30to80_BCtoE":
                return "/QCD_Pt_30_80_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_80to170_BCtoE":
                return "/QCD_Pt_80_170_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"
    if channel == "QCD_Pt_170to250_BCtoE":
                return "/QCD_Pt_170_250_BCtoE_TuneZ2star_8TeV_pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM"

    if channel == "QCD_HT_40_100_GJets":
                return "/GJets_HT-400ToInf_8TeV-madgraph/Summer12-PU_S7_START52_V9-v1/AODSIM"
    if channel == "QCD_HT_100_200_GJets":
                return "/GJets_TuneZ2_100_HT_200_7TeV-madgraph/Summer11-PU_S4_START42_V11-v1/AODSIM"
    if channel == "QCD_HT_200_inf_GJets":
                return "/GJets_TuneZ2_200_HT_inf_7TeV-madgraph/Summer11-PU_S4_START42_V11-v1/AODSIM"
    if channel == "W1Jet":
        return "/W1Jet_TuneZ2_7TeV-madgraph-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM"
    if channel == "W2Jets":
        return "/W2Jets_TuneZ2_7TeV-madgraph-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM"
    if channel == "W3Jets":
        return "/W3Jets_TuneZ2_7TeV-madgraph-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM"
    if channel == "W4Jets":
        return "/W4Jets_TuneZ2_7TeV-madgraph-tauola/Summer11-PU_S4_START42_V11-v1/AODSIM"
    

    if channel == "Mu_v4":
        return "/SingleMu/Run2011A-PromptReco-v4/AOD"
    if channel == "Mu_May10":
        return "/SingleMu/Run2011A-May10ReReco-v4/AOD"
    if channel == "Mu_Aug05":
        return "/SingleMu/Run2011A-05Aug2011-v1/AOD"
    if channel == "MuHad_Aug05":
        return "/MuHad/Run2011A-05Aug2011-v1/AOD"
    if channel == "MuHad_Oct03":
        return "/MuHad/Run2011A-03Oct2011-v1/AOD"

    if channel == "Ele_May10":
        return "/SingleElectron/Run2011A-May10ReReco-v4/AOD"
    if channel == "EleHad_v4":
        return "/ElectronHad/Run2011A-PromptReco-v4/AOD"
    if channel == "EleHad_Aug05":
        return "/ElectronHad/Run2011A-05Aug2011-v1/AOD"
    if channel == "EleHad_Oct03":
        return "/ElectronHad/Run2011A-03Oct2011-v1/AOD"


    #        return "/W2Jets_TuneZ2_7TeV-madgraph-tauola/Fall11-PU_S6_START42_V14B-v1/AODSIM"

def entriesmap(channel):
    if channel == "TTBar" or channel == "TWChannel" or channel == "TbarWChannel" or channel == "SChannel" or channel == "SbarChannel" or channel == "WW" or channel == "WZ" or channel == "ZZ" or "QCD_HT" in channel or channel == "TbarChannel_Q2Up" or channel == "TbarChannel_Q2Down" or channel == "TChannel_Q2Down" or channel == "TChannel_Q2Up":
        return 50000

    if "0100" in channel or "unphys" in channel:
        return 10000

    if "TToBMuNu" in channel or "TToBENu" in channel or "TToBTauNu" in channel:
        return 10000

    if channel == "TTBar_Q2Down" or channel == "TTBar_Q2Up" or channel == "TTBar_MatchingDown" or channel == "TTBar_MatchingUp"  or channel == "QCDMuBig":
        return 50000

    if channel == "TTBar_MassDown" or channel == "TTBar_MassUp":
        return 10000

    if channel == "TChannel_MassDown" or channel == "TChannel_MassUp" or channel == "TbarChannel_MassUp" or channel == "TbarChannel_MassDown":
        return 5000

    if channel == "TTBarFullLep" or channel == "TTBarSemiLep":
        return 50000

    if ("TWChannel" in channel or "TbarWChannel" in channel or "TWChannel" in channel or "TbarWChannel" in channel) and ("had" in channel or "FullLep" in channel):
        return 50000

    if channel == "TChannel" or channel == "TbarChannel":
        return 25000
    
    if channel == "WJets" or channel == "ZJets" or channel == "QCDMu" or "Pt_20to30" in channel or "Pt_30to80" in channel:
        return 50000
    if channel == "WJetsBig":
        return 120000
    if channel == "WJets_MatchingDown" or channel == "WJets_MatchingUp" or channel == "WJets_Q2Down" or channel == "WJets_Q2Up":
        return 120000

    if channel == "W1Jet":
        return 200000
    if channel == "W2Jets":
        return 100000
    if channel == "W3Jets":
        return 80000
    if channel == "W4Jets":
        return 80000

    if "Pt_80to170" in channel or "Pt_170to250" in channel:
        return 50000
    if "May10" in channel:
        return 50
    if "v4" in channel:
        return 140
    if "Aug05" in channel or "Oct03" in channel:
        return 250
#Function to replace a sequence of characters channelOld to channelNew in a file 
def changeChannel(fileName,channelOld,channelNew): 
    print " Channel test " + channelNew
    channelToReplace = channelNew
    file = open(fileName)
    lines = file.readlines()
    #             channelNew+"_crab.cfg","w") 
    name = fileName.replace(channelOld,channelToReplace)
    print name
    o = open(name,"w")
    for line in lines:
        if "user_remote_dir" in line or "pset" in line or "output_file" in line or "ui_working_dir" or "ChannelName" in line:
            words = line.split()
            for word in words:
                if channelOld in word:  
                    line = line.replace(word,word.replace(channelOld,channelToReplace))
        if "datasetpath" in line and not "#datasetpath" in line:
            line = "datasetpath = " + datasetmap(channelNew) +"\n"
        if "events_per_job" in line and not "#events_per_job" in line :
            line = "events_per_job ="+ str(entriesmap(channelToReplace))
        if "lumis_per_job" in line and not "#lumis_per_job" in line :
            line = "lumis_per_job ="+ str(entriesmap(channelToReplace))
        o.write(line)   
    o.close()
    return o

#Implementation of the loop part:

#Channel in the original file
startChannel = "TChannel"#channels[0]

f= open(fileName)
f2= open(fileName2)

tmpName = "temp.py"
shutil.copy(fileName,tmpName)

for channel in channels:

    channelOld = startChannel
    
    cfg_file = changeChannel(fileName,channelOld,channel)
    pset_file = changeChannel(fileName2,channelOld,channel)

#    os.system("bg") 
#    os.system('rm '+channel+'_cfg.py' ) 

os.system('rm '+tmpName) 
#changeChannel(f,aChannel,startChannel)

#os.system(command)



