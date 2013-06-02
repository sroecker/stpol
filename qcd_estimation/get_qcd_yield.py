#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *
from ROOT import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from FitConfig import FitConfig
from util_scripts import *
from DataLumiStorage import *

try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
    sys.exit(1)

def get_yield(var, filename, cutMT, mtMinValue, fit_result):
    infile = "fits/"+var.shortName+"_fit_"+filename+".root"
    f = TFile(infile)
    #QCDRATE = fit_result.qcd
    hQCD = f.Get(var.shortName+"__qcd")
    #print fit_result
    if cutMT:
        bin1 = hQCD.FindBin(mtMinValue)
        bin2 = hQCD.GetNbinsX() + 1
        #print hQCD.Integral(), y.Integral()
        error = array('d',[0.])
        y = hQCD.IntegralAndError(bin1,bin2,error)
        return (y, error[0])
        #return (hQCD.Integral(6,20), hQCD.Integral(6,20)*(fit_result.qcd_uncert/fit_result.qcd))
    else:
        return (hQCD.Integral(), hQCD.Integral()*(fit_result.qcd_uncert/fit_result.qcd))

def get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup):
    (y, fit) = get_qcd_yield(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)
    return y

def get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup):
    fit = Fit()    
    make_histos_with_cuts(var, cuts, dataGroup, MCGroups, systematics, lumis, openedFiles, fit, useMCforQCDTemplate, QCDGroup)
    fit_qcd(var, cuts.name, fit)
    return (get_yield(var, cuts.name, cutMT, mtMinValue, fit), fit)

#Run as ~andres/theta_testing/utils2/theta-auto.py get_qcd_yield.py
if __name__=="__main__":
    #channel = "ele"
    channel = "mu"

    print "QCD estimation in " + channel + " channel"
    
    #Specify variable on which to fit
    if channel == "mu":
        var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")    
    elif channel == "ele":
        var = Variable("met", 0, 200, 20, "MET", "MET")
    else:
        print "Set either 'ele' or 'mu' as channel"
        sys.exit(1)
    
    #Do you want to get the resulting yield after a cut on the fitted variable?
    if channel == "mu":
        cutMT = True
    if channel == "ele":
        cutMT = False

    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate
    mtMinValue = 50.01 # M_T>50
    
    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.

    fit_regions = ["final_selection", "2j0t"]

    cuts = FitConfig("final_selection")
    
    if channel == "ele":
        cuts.setTrigger("1") #  || HLT_Ele27_WP80_v9==1 || HLT_Ele27_WP80_v8==1")
        cuts.setIsolationCut("el_mva > 0.9 & el_reliso < 0.1")
        cuts.setAntiIsolationCut("el_reliso > 0.1 & el_reliso < 0.5")
        cuts.setAntiIsolationCutUp("el_reliso > 0.11 & el_reliso < 0.55") # check +-10% variation
        cuts.setAntiIsolationCutDown("el_reliso > 0.09 & el_reliso < 0.45")
        lepton_weight = "*electron_triggerWeight*electron_IDWeight"
    if channel == "mu":
        lepton_weight = "*muon_TriggerWeight*muon_IsoWeight*muon_IDWeight"
        cuts.setTrigger("1")
    
    #cuts.setTrigger("1")
    #cuts.setWeightMC("pu_weight*b_weight_nominal"+lepton_weight)
    
    
    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()

    #Luminosities for each different set of data have to be specified.
    #Now only for iso and anti-iso. In the future additional ones for systematics.
    #See DataLumiStorage for details if needed

    if channel == "mu":
        dataLumiIso = 19739
        dataLumiAntiIso = 19739

    if channel == "ele":
        dataLumiIso = 19728
        dataLumiAntiIso = 19728
        
    lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)
    
    #Different groups are defined in init_data. Select one you need or define a new one.
    if channel == "mu":
        dataGroup = dgDataMuons
    if channel == "ele":
        dataGroup = dgDataElectrons

    #MC Default is a set muon specific groups with inclusive t-channel for now. MC Groups are without QCD
    #MCGroups = MC_groups_noQCD_InclusiveTCh
    MCGroups = MC_groups_noQCD_AllExclusive
    
    #Do you want to get QCD template from MC?
    useMCforQCDTemplate = False

    #QCD MC group from init_data
    QCDGroup = None #can change to dgQCDMu, for example

    #Open files
    systematics = ["Nominal", "En", "Res", "UnclusteredEn"]
    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually

    if channel == "mu":
        base_path = "/home/andres/single_top/stpol/out_step3_05_29"
    if channel == "ele":
        base_path = "~liis/SingleTopJoosep/stpol/out_step3_05_28_19_36/ele"        

    paths = generate_paths(systematics, base_path)
    #For example:
    paths["iso"]["Nominal"] = base_path+"/iso/Nominal/"
    paths["antiiso"]["Nominal"] = base_path+"/antiiso/Nominal/"
    #Then open files    
    print "opening data and MC files"
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)
    
    #Before Running make sure you have 'templates' and 'fits' subdirectories where you're running
    #Root files with templates and fit results will be saved there.
    #Name from FitConfig will be used in file names    
    ((y, error), fit) = get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)
    #print cuts
    print "Selection: %s" % cuts.name
    print "QCD yield in selected region: ", y, "+-", error
    print "Total: QCD: %.2f +- %.2f" % (fit.qcd, fit.qcd_uncert)
    print "W+Jets: %.2f +- %.2f, ratio to template: %.2f" % (fit.wjets, fit.wjets_uncert, fit.wjets/fit.wjets_orig)
    print "Other MC: %.2f +- %.2f, ratio to template: %.2f" % (fit.nonqcd, fit.nonqcd_uncert, fit.nonqcd/fit.nonqcd_orig)

    print "Fit info:"
    print fit
    #make plot
    dataHisto = dataGroup.getHistogram(var,  "Nominal", "iso", cuts.name)
    plot_fit(var, cuts, dataHisto, fit)
