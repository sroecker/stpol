#!/usr/bin/python
# -*- coding: utf-8 -*-

from ROOT import *
from cuts import *
from plotting import *

#from util_scripts import *
#from Variable import *
#from DatasetGroup import *
#from FitResult import *
#from fitresults_costheta import *
#from init_data_53_v3 import *


def make_histos_with_cuts(var, n_jets, n_tags, other_cuts, anti_iso_cuts, fit, systematics, open_files, filename):
   QCD_FACTOR = 10000.
    
   syst_type = ["Up", "Down"]

   stacks =  {}
   #Iso region
   for s in systematics:
      if s == "":
         stack = make_stack(var, fit.getLabel(), MC_groups_noQCD, data_group, open_files, s, "iso", get_cuts_iso_mc_manual(other_cuts, n_jets, n_tags), get_cuts_iso_data_manual(other_cuts, n_jets, n_tags), "", fit.getLabel())
         stacks[var.name+s+"iso"] = stack
      else:
         for st in syst_type:
            stack = make_stack(var, fit.getLabel(), MC_groups_noQCD, data_group, open_files, s+st, "iso", get_cuts_iso_mc_manual(other_cuts, n_jets, n_tags), get_cuts_iso_data_manual(other_cuts, n_jets, n_tags), "", fit.getLabel())
            stacks[var.name+s+st+"iso"] = stack
         
   #print "Y"
   #Anti-iso region
   for s in systematics:
      if s == "":
         make_histogram(var, dgQCD, fit.getLabel(), open_files, s, "antiiso", get_cuts_antiiso_qcd_manual(other_cuts, anti_iso_cuts, n_jets, n_tags))                    
         make_histogram(var, dgData, fit.getLabel(), open_files, s, "antiiso", get_cuts_antiiso_data_manual(other_cuts, anti_iso_cuts, n_jets, n_tags))

         #make_histogram(var, branch, dgData, "50plus_stuff", open_files, s, "antiiso", cutsOrig+" && "+cutRelIso +" && mt_mu>50", "50plus")
         #make_histogram(var, branch, dgQCD, "50plus_stuff", open_files, s, "antiiso", weightsQCD + "*(" + cutsOrig+" && "+cutRelIso + " && mt_mu>50)", "50plus")
         
         stack = make_stack(var, fit.getLabel()+s, MC_groups_noQCD, dgData, 
                        open_files, s, "antiiso", get_cuts_antiiso_mc_manual(other_cuts, anti_iso_cuts, n_jets, n_tags), get_cuts_antiiso_data_manual(other_cuts, anti_iso_cuts, n_jets, n_tags), "", fit.getLabel())
         stacks[var.name+s+"antiiso"] = stack
         
         #Iso down
         make_histogram(var, dgQCD, fit.getLabel()+"iso down", open_files, s, "antiiso", get_cuts_antiiso_qcd_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_minus"), "_iso_minus")
         stack = make_stack(var, fit.getLabel()+s+"iso down", MC_groups_noQCD, dgData, open_files, s, "antiiso", 
                        get_cuts_antiiso_mc_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_minus"), get_cuts_antiiso_data_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_minus"), "", "_iso_minus"+fit.getLabel())
         stacks[var.name+s+"antiiso"+"_iso_minus"] = stack
         #make_histogram(var, branch, dgData, fit.getLabel()+"iso down", open_files, s, "antiiso", cutsData+" && "+cutRelIsoDown, "_iso_minus")

         #Iso Up
         make_histogram(var, dgQCD, fit.getLabel()+"iso up", open_files, s, "antiiso", get_cuts_antiiso_qcd_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_plus"), "_iso_plus")   
         stack = make_stack(var, fit.getLabel()+s+"iso up", MC_groups_noQCD, dgData, open_files, s, "antiiso", 
                        get_cuts_antiiso_mc_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_plus"), get_cuts_antiiso_data_manual(other_cuts, anti_iso_cuts, n_jets, n_tags, "iso_plus"), "", "_iso_plus"+fit.getLabel())
         stacks[var.name+s+"antiiso"+"_iso_plus"] = stack
         #make_histogram(var, dgData, fit.getLabel()+"iso up", open_files, s, "antiiso", cutsData+" && "+cutRelIsoUp,"_iso_plus")           
                    
   #Write out stuff 
   outfile = TFile("templates/"+var.shortName+"_templates_"+filename+".root", "recreate")
   outfile.cd()
           
   #non-QCD
   for s in systematics:
      if s == "":
         stack = stacks[var.name+s+"iso"]
         h1 = TH1D(var.shortName+"__nonqcd", var.shortName+"__nonqcd", var.bins, var.lbound, var.ubound)   
         for h in stack.GetHists():
            h1.Add(h)     
         h1.Write()
         print "MC integral", h1.Integral()
      else:
         for st in syst_type:
            if st == "Up":
               syst_string = "__"+s+"__plus"
            else:
               syst_string = "__"+s+"__minus"
            stack = stacks[var.name+s+st+"iso"]            
            h1 = TH1D(var.shortName+"__nonqcd"+syst_string, var.shortName+"__nonqcd"+syst_string, var.bins, var.lbound, var.ubound)   
            for h in stack.GetHists():
               h1.Add(h)
            h1.Write()
   #Data
   print dgData._histograms
   hData = dgData.getHistogram(var, "", "iso", fit.getLabel())
   hData.SetName(var.shortName+"__DATA")
   print "data integral", hData.Integral()
   hData.Write()
         
   #QCD
   if fit.isMC:
      for s in systematics:
         if s == "":
            hQCD = dgQCD.getHistogram(var, s, "antiiso")
            #hQCD2 = dgQCD.getHistogram(var, branch, s, "antiiso", "50plus")
            hQCD.SetName(var.shortName+"__qcd")
            print "QCD Integral", hQCD.GetEntries(), hQCD.Integral()
            #print "QCD Integral 50+", hQCD2.GetEntries(), hQCD2.Integral()
            hQCD.Write()
            hQCDisoUp = dgQCD.getHistogram(var, s, "antiiso", "_iso_plus")
            hQCDisoDown = dgQCD.getHistogram(var, s, "antiiso", "_iso_minus")
         else:
            for st in syst_type:
               if st == "Up":
                  syst_string = "__"+s+"__plus"
               else:
                  syst_string = "__"+s+"__minus"
               hQCD = dgQCD.getHistogram(var, s+st+"antiiso")
               hQCD.SetName(var.shortName+"__qcd"+syst_string)
               print "QCD integral "+s+st, hQCD.Integral()
               hQCD.Write()
   else:
      hQCD = dgData.getHistogram(var, s, "antiiso")
      """
      try:
         hQCD2 = dgData.getHistogram(var, branch, s, "antiiso", "50plus")
         #hQCD2.Scale(QCD_FACTOR/hQCD.Integral())
         #print "QCD 50plus integral", hQCD2.Integral(6,20)
         #(bs,v) = fit.res["qcd"]["beta_signal"][0]
         #print "QCD 50plus integral", bs*hQCD2.Integral(6,20)
         print "uncert=", fit.qcd_uncert/fit.qcd*bs*hQCD2.Integral(6,20)
      except KeyError:
         print "no fit result yet"
      except ZeroDivisionError:
         print "no fit result yet? - zero division"    
      """
      hQCD.SetName(var.shortName+"__qcd")               
      hQCDisoUp = dgData.getHistogram(var, s, "antiiso", "_iso_plus"+fit.getLabel())
      hQCDisoDown = dgData.getHistogram(var, s, "antiiso", "_iso_minus"+fit.getLabel())
               
      stack = stacks[var.name+"antiiso"]
      for h in stack.GetHists():
         hQCD.Add(h,-1)
                    
      stack = stacks[var.name+"antiiso_iso_plus"]    
      for h in stack.GetHists():
         hQCDisoUp.Add(h, -1)
                
      stack = stacks[var.name+"antiiso_iso_minus"]                
      for h in stack.GetHists():
         hQCDisoDown.Add(h, -1)
           
      if hQCD.Integral() > 0:
         hQCD.Scale(QCD_FACTOR/hQCD.Integral())
      if hQCDisoUp.Integral() > 0:
         hQCDisoUp.Scale(QCD_FACTOR/hQCDisoUp.Integral())
      if hQCDisoDown.Integral() > 0:
         hQCDisoDown.Scale(QCD_FACTOR/hQCDisoDown.Integral())
            
      print "QCD integral", hQCD.Integral()   
      hQCD.Write()
      hQCDisoUp.SetName(var.shortName+"__qcd__ISO__plus")
      hQCDisoDown.SetName(var.shortName+"__qcd__ISO__minus")
      print "QCD isoUp integral", hQCDisoUp.GetEntries(), hQCDisoUp.Integral()
      print "QCD isoDown integral", hQCDisoDown.GetEntries(), hQCDisoDown.Integral()
      hQCDisoUp.Write()
      hQCDisoDown.Write()
   
   outfile.Write()   
   outfile.Close()
    
def make_histos(var, fit, systematics, open_files):
   QCD_FACTOR = 1000.
    
   syst_type = ["Up", "Down"]

   #baseCuts += " && n_jets == 2"
   #baseCuts += " && n_tags == 1"
   
   #baseCuts += " && mt_mu>50"
   
   region = fit.getRegion()
   print fit.getLabel()
   print " "
   stacks =  {}

   #print "X"
   #Iso region
   for s in systematics:
      if s == "":
         stack = make_stack(var, fit.getLabel(), MC_groups_noQCD, data_group, open_files, s, "iso", get_cuts_iso_mc(fit), get_cuts_iso_data(fit), "", fit.getLabel())
         stacks[var.name+s+"iso"] = stack
      else:
         for st in syst_type:
            stack = make_stack(var, fit.getLabel(), MC_groups_noQCD, data_group, open_files, s+st, "iso", get_cuts_iso_mc(fit), get_cuts_iso_data(fit), "", fit.getLabel())
            stacks[var.name+s+st+"iso"] = stack
         
   #print "Y"
   #Anti-iso region
   for s in systematics:
      if s == "":
         make_histogram(var, dgQCD, fit.getLabel(), open_files, s, "antiiso", get_cuts_antiiso_qcd(fit))                    
         make_histogram(var, dgData, fit.getLabel(), open_files, s, "antiiso", get_cuts_antiiso_data(fit))

         #make_histogram(var, branch, dgData, "50plus_stuff", open_files, s, "antiiso", cutsOrig+" && "+cutRelIso +" && mt_mu>50", "50plus")
         #make_histogram(var, branch, dgQCD, "50plus_stuff", open_files, s, "antiiso", weightsQCD + "*(" + cutsOrig+" && "+cutRelIso + " && mt_mu>50)", "50plus")
         
         stack = make_stack(var, fit.getLabel()+s, MC_groups_noQCD, dgData, 
                        open_files, s, "antiiso", get_cuts_antiiso_mc(fit), get_cuts_antiiso_data(fit), "", fit.getLabel())
         stacks[var.name+s+"antiiso"] = stack
         
         #Iso down
         make_histogram(var, dgQCD, fit.getLabel()+"iso down", open_files, s, "antiiso", get_cuts_antiiso_qcd(fit, "iso_minus"), "_iso_minus")
         stack = make_stack(var, fit.getLabel()+s+"iso down", MC_groups_noQCD, dgData, open_files, s, "antiiso", 
                        get_cuts_antiiso_mc(fit, "iso_minus"), get_cuts_antiiso_data(fit, "iso_minus"), "", "_iso_minus"+fit.getLabel())
         stacks[var.name+s+"antiiso"+"_iso_minus"] = stack
         #make_histogram(var, branch, dgData, fit.getLabel()+"iso down", open_files, s, "antiiso", cutsData+" && "+cutRelIsoDown, "_iso_minus")

         #Iso Up
         make_histogram(var, dgQCD, fit.getLabel()+"iso up", open_files, s, "antiiso", get_cuts_antiiso_qcd(fit, "iso_plus"), "_iso_plus")   
         stack = make_stack(var, fit.getLabel()+s+"iso up", MC_groups_noQCD, dgData, open_files, s, "antiiso", 
                        get_cuts_antiiso_mc(fit, "iso_plus"), get_cuts_antiiso_data(fit, "iso_plus"), "", "_iso_plus"+fit.getLabel())
         stacks[var.name+s+"antiiso"+"_iso_plus"] = stack
         #make_histogram(var, dgData, fit.getLabel()+"iso up", open_files, s, "antiiso", cutsData+" && "+cutRelIsoUp,"_iso_plus")           
                    
   #Write out stuff   
   outfile = TFile("templates/"+var.shortName+"_templates_"+fit.getLabel()+".root", "recreate")
   outfile.cd()
           
   #non-QCD
   for s in systematics:
      if s == "":
         stack = stacks[var.name+s+"iso"]
         h1 = TH1D(var.shortName+"__nonqcd", var.shortName+"__nonqcd", var.bins, var.lbound, var.ubound)   
         for h in stack.GetHists():
            h1.Add(h)     
         h1.Write()
         print "MC integral", h1.Integral()
      else:
         for st in syst_type:
            if st == "Up":
               syst_string = "__"+s+"__plus"
            else:
               syst_string = "__"+s+"__minus"
            stack = stacks[var.name+s+st+"iso"]            
            h1 = TH1D(var.shortName+"__nonqcd"+syst_string, var.shortName+"__nonqcd"+syst_string, var.bins, var.lbound, var.ubound)   
            for h in stack.GetHists():
               h1.Add(h)
            h1.Write()
   #Data
   hData = dgData.getHistogram(var, "", "iso", fit.getLabel())
   hData.SetName(var.shortName+"__DATA")
   print "data integral", hData.Integral()
   hData.Write()
         
   #QCD
   if fit.isMC:
      for s in systematics:
         if s == "":
            hQCD = dgQCD.getHistogram(var, s, "antiiso")
            #hQCD2 = dgQCD.getHistogram(var, branch, s, "antiiso", "50plus")
            hQCD.SetName(var.shortName+"__qcd")
            print "QCD Integral", hQCD.GetEntries(), hQCD.Integral()
            #print "QCD Integral 50+", hQCD2.GetEntries(), hQCD2.Integral()
            hQCD.Write()
            hQCDisoUp = dgQCD.getHistogram(var, s, "antiiso", "_iso_plus")
            hQCDisoDown = dgQCD.getHistogram(var, s, "antiiso", "_iso_minus")
         else:
            for st in syst_type:
               if st == "Up":
                  syst_string = "__"+s+"__plus"
               else:
                  syst_string = "__"+s+"__minus"
               hQCD = dgQCD.getHistogram(var, s+st+"antiiso")
               hQCD.SetName(var.shortName+"__qcd"+syst_string)
               print "QCD integral "+s+st, hQCD.Integral()
               hQCD.Write()
   else:
      hQCD = dgData.getHistogram(var, s, "antiiso")
      """
      try:
         hQCD2 = dgData.getHistogram(var, branch, s, "antiiso", "50plus")
         #hQCD2.Scale(QCD_FACTOR/hQCD.Integral())
         #print "QCD 50plus integral", hQCD2.Integral(6,20)
         #(bs,v) = fit.res["qcd"]["beta_signal"][0]
         #print "QCD 50plus integral", bs*hQCD2.Integral(6,20)
         print "uncert=", fit.qcd_uncert/fit.qcd*bs*hQCD2.Integral(6,20)
      except KeyError:
         print "no fit result yet"
      except ZeroDivisionError:
         print "no fit result yet? - zero division"    
      """
      hQCD.SetName(var.shortName+"__qcd")               
      hQCDisoUp = dgData.getHistogram(var, s, "antiiso", "_iso_plus"+fit.getLabel())
      hQCDisoDown = dgData.getHistogram(var, s, "antiiso", "_iso_minus"+fit.getLabel())
               
      stack = stacks[var.name+"antiiso"]
      for h in stack.GetHists():
         hQCD.Add(h,-1)
                    
      stack = stacks[var.name+"antiiso_iso_plus"]    
      for h in stack.GetHists():
         hQCDisoUp.Add(h, -1)
                
      stack = stacks[var.name+"antiiso_iso_minus"]                
      for h in stack.GetHists():
         hQCDisoDown.Add(h, -1)
           
      if hQCD.Integral() > 0:
         hQCD.Scale(QCD_FACTOR/hQCD.Integral())
      if hQCDisoUp.Integral() > 0:
         hQCDisoUp.Scale(QCD_FACTOR/hQCDisoUp.Integral())
      if hQCDisoDown.Integral() > 0:
         hQCDisoDown.Scale(QCD_FACTOR/hQCDisoDown.Integral())
            
      print "QCD integral", hQCD.Integral()   
      hQCD.Write()
      hQCDisoUp.SetName(var.shortName+"__qcd__ISO__plus")
      hQCDisoDown.SetName(var.shortName+"__qcd__ISO__minus")
      print "QCD isoUp integral", hQCDisoUp.GetEntries(), hQCDisoUp.Integral()
      print "QCD isoDown integral", hQCDisoDown.GetEntries(), hQCDisoDown.Integral()
      hQCDisoUp.Write()
      hQCDisoDown.Write()
   
   outfile.Write()   
   outfile.Close()
