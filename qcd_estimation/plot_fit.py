#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

from ROOT import *

from init_data import *
from Variable import *
from DatasetGroup import *
from Fit import *
#from fitresults_costheta import *
from plot_settings import *
from plotting import make_histogram, make_stack
from cuts import *
from copy import deepcopy
from DataLumiStorage import *


def plot_fit(var, fit_result, open_files):
   canvases = []
   infile = "fits/"+var.shortName+"_fit_"+fit_result.getLabel()+".root"
   f = TFile(infile)
   open_files[fit_result.getLabel()] = f
   
   print fit_result.getLabel()
   outfile = TFile("temp.root", "recreate")   
   outfile_name = "fit_plots/"+var.shortName+"_Fit_"+fit_result.getLabel()
   
   print fit_result
   QCDRATE = fit_result.qcd
   QCDRATE_UP = fit_result.qcd + fit_result.qcd_uncert
   QCDRATE_DOWN = fit_result.qcd - fit_result.qcd_uncert
   NONQCDRATE = fit_result.nonqcd
   NONQCDRATE_UP = fit_result.nonqcd + fit_result.nonqcd_uncert
   NONQCDRATE_DOWN = fit_result.nonqcd - fit_result.nonqcd_uncert
        
   print QCDRATE, QCDRATE_UP, QCDRATE_DOWN, NONQCDRATE, NONQCDRATE_UP,NONQCDRATE_DOWN
      
   cuts = get_cuts_iso_data(fit_result)
   fit_result_all_mtw = deepcopy(fit_result)
   fit_result_all_mtw.extra = ""
   cuts_antiiso = get_cuts_antiiso_data(fit_result_all_mtw)
   region = "2J_"+str(fit_result.tags)+"T"
   print "cuts " +cuts
   print "antiiso",cuts_antiiso

   lumiABIso = 5140.
   lumiCIso = 6451.
   lumiDIso = 6471.
   dataLumiIso = lumiABIso + lumiCIso + lumiDIso
   lumiABAntiIso = 5140.
   lumiCAntiIso = 6451.
   lumiDAntiIso = 6471.
   dataLumiAntiIso = lumiABAntiIso + lumiCAntiIso + lumiDAntiIso   
   lumis = DataLumiStorage(dataLumiIso, dataLumiAntiIso)

   make_histogram(var, dgDataMuons, "Data", open_files, lumis, "Nominal", "iso", cuts, "plot")
   make_histogram(var, dgDataMuons, "QCD", open_files, lumis, "Nominal", "antiiso", cuts_antiiso)
      
   cst = TCanvas("Histogram_"+fit_result.getLabel(),fit_result.getLabel(),10,10,1800,1000)
   cst.SetLeftMargin(1)
   cst.SetRightMargin(0.2)
        
   gStyle.SetOptStat(0)
   hNonQCD = TH1D(f.Get(var.shortName+"__nonqcd"))
   hNonQCD.SetTitle("Non-QCD")   
   hNonQCD.SetLineColor(kRed)
   hNonQCD.SetLineWidth(3)
      
   hNonQCDp=TH1D(hNonQCD)
   hNonQCDp.Scale(NONQCDRATE_UP/NONQCDRATE)
   hNonQCDm=TH1D(hNonQCD)
   hNonQCDm.Scale(NONQCDRATE_DOWN/NONQCDRATE)
      
   hNonQCDp.SetLineColor(kOrange)
   hNonQCDp.SetLineWidth(2)
   hNonQCDp.SetTitle("non-QCD + 1 sigma")
   hNonQCDm.SetLineColor(kOrange)
   hNonQCDm.SetLineWidth(2)
   hNonQCDm.SetTitle("non-QCD - 1 sigma")
      
   hData = dgDataMuons.getHistogram(var,  "Nominal", "iso", "plot")
   hData.SetNameTitle(var.shortName+"__DATA", "Data")
   hData.SetMarkerStyle(20)

   print "data integral: ",hData.Integral()
      
     
   hQCD = f.Get(var.shortName+"__qcd")
   hQCD.SetNameTitle(var.shortName+"__qcd", "QCD")
   hQCD.SetLineColor(kYellow)
   hQCD.SetLineWidth(3)      
      
   hQCDp=TH1D(hQCD)
   hQCDp.Scale(QCDRATE_UP/QCDRATE)
   hQCDm=TH1D(hQCD)   
   hQCDm.Scale(QCDRATE_DOWN/QCDRATE)
      
   hQCDp.SetLineColor(kGreen)
   hQCDp.SetLineWidth(2)
   hQCDp.SetTitle("QCD + 1 sigma")
   hQCDm.SetLineColor(kGreen)
   hQCDm.SetLineWidth(2)
   hQCDm.SetTitle("QCD - 1 sigma")
      
   hTotal=TH1D(hNonQCD)
   hTotal.Add(hQCD)
   hTotal.SetLineColor(kBlue)
   hTotal.SetLineWidth(2)
   hData.SetAxisRange(0,fit_result.maxY,"Y")
   hData.GetXaxis().SetTitle(var.displayName)
   hData.GetYaxis().SetTitleFont(42)
   hData.GetYaxis().SetTitleOffset(1.)
   hData.GetXaxis().SetTitleFont(42)      
   #hTotal.Draw("")
   title = fit_result.getTitle()
   hData.SetMarkerStyle(20)
   hData.Draw("E1")
   hNonQCDp.Draw("same")
   hQCD.Draw("same")
   hNonQCD.Draw("same")
   hNonQCDm.Draw("same")
   hQCDp.Draw("same")
   hQCDm.Draw("same")
   hTotal.Draw("same")
   hData.SetTitle("QCD fit, "+title)
   hData.Draw("E1 same")
   leg = TLegend(0.81,0.27,0.93,0.90)
   leg.SetTextSize(0.037)
   leg.SetBorderSize(0)
   leg.SetLineStyle(0)
   leg.SetTextSize(0.04)
   leg.SetFillStyle(0)
   leg.SetFillColor(0)
       
   leg.AddEntry(hData,"Data","pl")
   leg.AddEntry(hNonQCD,"Non-QCD","f")
   leg.AddEntry(hNonQCDp,"Non-QCD #pm 1 #sigma","f")
   leg.AddEntry(hQCD,"QCD","f")
   leg.AddEntry(hQCDp,"QCD #pm 1 #sigma","f")
   leg.AddEntry(hTotal, "QCD + Non-QCD", "f")
   leg.Draw()
          
   print hNonQCD.Integral(), hData.Integral(), hQCD.Integral(), hTotal.Integral(), hQCDp.Integral(), hQCDm.Integral()
   cst.Update()
   hQCDShape = dgDataMuons.getHistogram(var,  "Nominal", "antiiso")
   stack = make_stack(var, fit_result.getLabel(), MC_groups_noQCD, dgDataMuons, 
                        open_files, "Nominal", "antiiso", lumis, get_cuts_antiiso_mc(fit_result), get_cuts_antiiso_data(fit_result), "", fit_result.getLabel())
   for h in stack.GetHists():
      hQCDShape.Add(h,-1)
   for i in range(50):
      events = hQCDShape.GetBinContent(i)
      if events < 0:
         hQCDShape.SetBinContent(i, 0)  

   if fit_result.extra == "mtwMass50":
      integral = hQCDShape.Integral(0,5)
   elif fit_result.extra == "mtwMass70":
      integral = hQCDShape.Integral(0,8)
   elif fit_result.extra == "mtwMass20plus":
      integral = hQCDShape.Integral(3,20)
   else:
      integral = hQCDShape.Integral()
   print hQCDShape.Integral(), integral
   hQCDShape.Scale(QCDRATE/(integral))
   print "QCD yield mtwMass>50: ",hQCD.Integral(6,20)
   if hQCD.Integral()>0:
      print "uncert= ", (hQCD.Integral(6,20)/hQCD.Integral())*(QCDRATE_UP-QCDRATE)
   print "QCD yield mtwMass>50 from original shape: ",hQCDShape.Integral(6,20)
   print hQCDShape.Integral(), hQCDShape.Integral(6,20), hQCDShape.Integral(0,5)
   print "uncert= ", (hQCDShape.Integral(6,20)/hQCDShape.Integral())*(QCDRATE_UP-QCDRATE)
   #print "QCD yield mtwMass<50: ",hQCD.Integral(0,5)#,hQCD.Integral(0,6)
   pv = hData.Chi2Test(hTotal,"UW P")
   #hData.Chi2Test(hTotal,"WU P")
   #hTotal.Chi2Test(hData,"UW P")
   print "p-val:",pv
   cst.SaveAs(outfile_name+".png")
   cst.SaveAs(outfile_name+".pdf")
   cst.Draw()
   return cst

