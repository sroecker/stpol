#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from FitConfig import *
from DataLumiStorage import *
from get_qcd_yield import *

def select_fits():
   fits = []
   #fits.append(res_2J_0T)
   #fits.append(res_2J_1T)
   #fits.append(res_2J_1T_SB)
   fits.append(res_2J_1T_SR)
   #fits.append(res_2J_1T_SR_Mu)
   #fits.append(res_2J_0T_MC)
   #fits.append(res_2J_1T_MC)
   #fits.append(res_2J_1T_SR_MC)
   #fits.append(res_2J_1T_SB_MC)

   #fits.append(res_2J_1T_SR_mtwMass50)
   #fits.append(res_2J_1T_SR_mtwMass20plus)
   #fits.append(res_2J_1T_SR_mtwMass70)
   """fits.append(res_2J_1T_SR_iso_0_3_plus)
   fits.append(res_2J_1T_SR_iso_0_5_plus)"""
   return fits

def select_cuts():
    cuts = []
    base = "pt_lj>40 && pt_bj>40 && abs(eta_lj)>2.5 && n_jets == 2 && n_tags == 1 && rms_lj<0.025"
    baseCuts = " && top_mass < 220 && top_mass > 130 "
    cutFinal = FitConfig("2J_1T_SR")
    cutFinal.setBaseCuts(base+baseCuts)
    cuts.append(cutFinal)
    return cuts

def do_fit(var,fit, systematics, open_files):
   make_histos(var, fit, systematics, open_files)
   qcd_yield=fit_qcd(fit)
   print fit.getLabel(), "yield:", qcd_yield
   print fit.result



if __name__=="__main__":
#    channel = "ele"
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
    cutMT = True
    #If yes, specify minumum value for the variable the cut. Obviously change to MET for electrons
    #Remember that the cut should be on the edge of 2 bins, otherwise the result will be inaccurate
    mtMinValue = 50.01 # M_T>50
    
    #Use Default cuts for final selection. See FitConfig for details on how to change the cuts.
    cuts = FitConfig("final_selection")
    #For example:  
    
    #Recreate all necessary cuts after manual changes
    cuts.calcCuts()

    dataLumiIso = 19739
    dataLumiAntiIso = 19739
    lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)
    
    dataGroup = dgDataMuons

    #MC Default is a set muon specific groups with inclusive t-channel for now. MC Groups are without QCD
    #MCGroups = MC_groups_noQCD_InclusiveTCh
    MCGroups = MC_groups_noQCD_AllExclusive
    
    #Do you want to get QCD template from MC?
    useMCforQCDTemplate = False

    #QCD MC group from init_data
    QCDGroup = None #can change to dgQCDMu, for example

    #Open files
    systematics = ["Nominal"] #Systematics to be added in the future
    #Generate path structure as base_path/iso/systematic, see util_scripts
    #If you have a different structure, change paths manually

    base_path = "/home/andres/single_top/stpol/out_step3_05_29"
    
    paths = generate_paths(systematics, base_path)
    #For example:
    paths["iso"]["Nominal"] = base_path+"/iso/Nominal/"
    paths["antiiso"]["Nominal"] = base_path+"/antiiso/Nominal/"
    #Then open files    
    print "opening data and MC files"
    openedFiles = open_all_data_files(dataGroup, MCGroups, QCDGroup, paths)
    
    cutconfs = select_cuts()
    canvases = []   
    for cuts in cutconfs: 
        cuts.setTrigger("1")
        cuts.calcCuts()
        ((y, error), fit) = get_qcd_yield_with_fit(var, cuts, cutMT, mtMinValue, dataGroup, lumis, MCGroups, systematics, openedFiles, useMCforQCDTemplate, QCDGroup)
        print "QCD yield with selection: %s" % cuts.name
        print y, "+-", error
        #clear_histos(data_group, mc_groups)
        dataHisto = dataGroup.getHistogram(var,  "Nominal", "iso", cuts.name)
        canvases.append(plot_fit(var, cuts, dataHisto, fit))
        clear_histos(dataGroup, MCgroups)
