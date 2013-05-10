#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *

from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from Fit import *


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

def do_fit(var,fit, systematics, open_files):
   make_histos(var, fit, systematics, open_files)
   qcd_yield=fit_qcd(fit)
   print fit.getLabel(), "yield:", qcd_yield
   print fit.result

if __name__=="__main__":
   #plot = True
   isos = ["iso", "antiiso"]
   systematics = [""]
   #syst = ["noSyst"]#, "JES", "JER", "UnclusteredMET"]   
     
   path = input_path 
   open_files = open_all_data_files(data_group, mc_groups, isos, systematics, path)
   
   var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")
   #var = Variable("cosThetaLightJet_cosTheta", -1,1, 5, "cosTheta", "cos(#theta^{* })")
   canvases = []   
   fits = select_fits()
   for fit in fits:
      do_fit(var, fit, systematics, open_files)
      clear_histos(data_group, mc_groups)
      canvases.append(plot_fit(var, fit, open_files))
      clear_histos(data_group, mc_groups)
