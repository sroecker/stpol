#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys,os
from theta_auto import *
from ROOT import *

#Add theta to path
sys.path.insert(1,"/home/andres/theta_testing/utils2/theta_auto/")   
sys.path.insert(2,"/home/andres/theta_testing/utils2/")
sys.path.insert(3,"/home/andres/theta_testing/utils/theta_auto/")
sys.path.insert(4,"/home/andres/single_top/stpol/qcd_estimation/")


from make_input_histos import *
from fit_with_theta import fit_qcd
from plot_fit import plot_fit
from Fit import Fit

def get_yield(var, fit_result, cutMT, filename):
   infile = "fits/mtwMass_fit_"+filename+".root"
   f = TFile(infile)   
   #QCDRATE = fit_result.qcd
   
   hQCD = f.Get(var.shortName+"__qcd")
   if cutMT:
      return (hQCD.Integral(6,20), hQCD.Integral(6,20)*(fit_result.qcd_uncert/fit_result.qcd))
   else:
      return (hQCD.Integral(), hQCD.Integral()*(fit_result.qcd_uncert/fit_result.qcd))

def get_qcd_yield(n_jets, n_tags, cutMT, other_cuts):
   isos = ["iso", "antiiso"]
   systematics = [""]
   path = input_path 
   open_files = open_all_data_files(data_group, mc_groups, isos, systematics, path)
   
   var = Variable("mt_mu", 0, 200, 20, "mtwMass", "m_{T }")
   filename = "temp_for_yield"
   fit = Fit()
   make_histos_with_cuts(var, n_jets, n_tags, other_cuts, fit, systematics, open_files, filename)
   fit_qcd(fit, filename)
   return get_yield(var, fit, cutMT, filename)

if __name__=="__main__":
   n_jets = 2
   n_tags = 1
   cutMT = True
   other_cuts = "pt_lj>40 && pt_bj>40"
   other_cuts += " && abs(eta_lj)>2.5" 
   other_cuts += " && (top_mass < 220 && top_mass > 130)"
   other_cuts += " && rms_lj<0.025"
   (y, error) = get_qcd_yield(n_jets, n_tags, cutMT, other_cuts)
   print y, "+-", error
