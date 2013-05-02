#from plots import *
#from plots import draw_stack
from init_data import *
#from plot_settings import *
from util_scripts import *
from Variable import *
from ROOT import *

def make_stack(var, stackName, MC_groups, data_group, open_files, syst, iso, cutsMC, cutsData, extra = ""):
   make_histograms(var, MC_groups, data_group, open_files, syst, iso, cutsMC, cutsData, extra)
   stack = THStack("Stack"+var.name+syst+iso, stackName)
   #print "making stack "+syst
   for group in MC_groups:     
      his = TH1D(group.getHistogram(var, syst, iso, extra))
      #print str(his.GetFillColor()) +" "+str(group.getColor())
      his.SetFillColor(group.getColor())
      #print "B "+str(his.GetFillColor()) +" "+str(group.getColor())
      his.SetLineWidth(1)
      stack.Add(his)
   return stack

def draw_stack(var, stack, MC_groups, data_group, syst="", iso="iso", name="", maxY=10000, save=True):
   cst = TCanvas("Histogram_"+var.name,"_"+var.name,10,10,1800,1000)
   gROOT.SetStyle("Plain")
   gStyle.SetOptStat(1000000000)
   cst.SetLeftMargin(1)
   cst.SetRightMargin(0.2)
           
   stack_data = data_group.getHistogram(var, syst, iso)
   #stack_data.Draw("E1 same")
   
   #stack_data.SetMaximum(800)   
   #stack.SetDrawOption()
   #stack.Draw("")
   #stack.SetDrawOption("")
   stack_data.Draw("E1")
   stack.Draw("same hist")
   stack_data.SetAxisRange(0,maxY,"Y")  
   stack_data.SetMarkerStyle(20)     
   stack_data.Draw("E1 same")
   #print "data ",stack_data.Integral()
   
   stack_data.GetXaxis().SetTitle(var.displayName)   

   leg = TLegend(0.81,0.27,0.93,0.90)
   leg.SetTextSize(0.037)
   leg.SetBorderSize(0)
   leg.SetLineStyle(0)
   leg.SetTextSize(0.04)
   #leg.SetFillStyle(0)
   leg.SetFillColor(0)
       
   leg.AddEntry(stack_data,"Data","pl")
   #gStyle.Reset()
   for group in MC_groups:
      group.getHistogram(var, syst, iso).SetFillColor(group.getColor())
      #print group.getHistogram(var, branch,label).GetFillColor()
      leg.AddEntry(group.getHistogram(var, syst, iso),group.getName(),"f")
        
   leg.Draw()


   cst.Update()
   cst.SaveAs("plots/stack_"+var.name+"_"+name+"_"+syst+"_"+iso+".png")
   cst.SaveAs("plots/stack_"+var.name+"_"+name+"_"+syst+"_"+iso+".pdf")
   return cst

def draw_final(var, stack, MC_groups, data_group, syst="", iso="iso", name="", maxY=10000, save=True):
   cst = TCanvas("Histogram_"+var.name,"_"+var.name,10,10,1800,1000)
   gROOT.SetStyle("Plain")
   gStyle.SetOptStat(1000000000)
   cst.SetLeftMargin(1)
   cst.SetRightMargin(0.2)
           
   stack_data = data_group.getHistogram(var, syst, iso)
   #stack_data.Draw("E1 same")
   
   #stack_data.SetMaximum(800)   
   #stack.SetDrawOption()
   #stack.Draw("")
   #stack.SetDrawOption("")
   stack_data.Draw("E1")
   stack.Draw("same hist")
   stack_data.SetAxisRange(0,maxY,"Y")
   stack_data.SetMarkerStyle(20)       
   stack_data.Draw("E1 same")
   #print "data ",stack_data.Integral()
   
   stack_data.GetXaxis().SetTitle(var.displayName)   

   leg = TLegend(0.81,0.27,0.93,0.90)
   leg.SetTextSize(0.037)
   leg.SetBorderSize(0)
   leg.SetLineStyle(0)
   leg.SetTextSize(0.04)
   #leg.SetFillStyle(0)
   leg.SetFillColor(0)
       
   leg.AddEntry(stack_data,"Data","pl")
   #gStyle.Reset()
   for group in MC_groups:
      group.getHistogram(var, syst, iso).SetFillColor(group.getColor())
      #print group.getHistogram(var, branch,label).GetFillColor()
      leg.AddEntry(group.getHistogram(var, syst, iso),group.getName(),"f")
      
   qcd_histo = data_group.getHistogram(var, syst, "antiiso")
   qcd_histo.SetLineColor(dgQCD.getColor())
   qcd_histo.SetFillColor(dgQCD.getColor())
   leg.AddEntry(qcd_histo,"QCD","f")     
   leg.Draw()

   cst.Update()
   cst.SaveAs("plots/final_plot_"+var.name+".png")
   cst.SaveAs("plots/final_plot_"+var.name+".pdf")
   return cst


def make_histograms(var, MC_groups, data_group, open_files, syst, iso, cutsMC, cutsData, extra = ""):
   all_groups = []
   all_groups.extend(MC_groups)
   total = 0
   if data_group is not None:
      all_groups.append(data_group)
   for group in all_groups:
      name = group.getName()
      histo_name = name+"_"+var.name+"_"+syst+"_"+iso+"_"+extra
      #print "name",histo_name
      h = TH1D(histo_name, group.getTitle(), var.bins, var.lbound, var.ubound)
      h.Sumw2()
      h.SetLineColor(group.getColor())
      h.SetLineWidth(2)
      for ds in group.getDatasets():
         if(True):#ds.hasBranch(branch) or ds.isMC()): #data???
            his_name = "histo"+"_"+ds.getName()+"_"+var.name+"_"+syst+iso+"_"+extra
            his = TH1D(his_name, his_name, var.bins, var.lbound, var.ubound)
            his.Sumw2()
            f = ds.getFile(syst, iso)
            tdir = f.Get("trees")
            #print ds.getName()+" "+ds.getTree()+"_"+syst+"_"+branch.name
            mytree = tdir.Get("Events")
            if group.isMC():
               weight = cutsMC               
            else:
               weight = cutsData
            #print "weight", weight
            mytree.Project(his_name, var.name, weight,"same")
            if group.isMC():
               his.Scale(ds.scaleToData(getDataLumi(iso)))               
            else:
               #print group, ds.preScale()
               his.Scale(ds.preScale())
            h.Add(his)
      #print group.getName(), var.name, syst, iso, h.GetEntries(), h.Integral()      
      group.addHistogram(h, var, syst, iso, extra)
      if group.isMC():
         total+=h.Integral()
   print "total MC",total

def getDataLumi(iso):
   if iso == "iso":
      return dataLumiIso
   elif iso == "antiiso":
      return dataLumiAntiIso

def make_histogram(var, group, title, open_files, syst="", iso="iso", weight="1", extra=""):
   name = group.getName()
   histo_name = name+"_"+var.name+"_"+syst+"_"+extra
   h = TH1D(histo_name, title, var.bins, var.lbound, var.ubound)
   h.Sumw2()
   h.SetLineColor(group.getColor())
   h.SetLineWidth(2)   
   for ds in group.getDatasets():
         his_name = "histo"+"_"+ds.getName()+"_"+var.name+"_"+syst+iso+extra
         his = TH1D(his_name, his_name, var.bins, var.lbound, var.ubound)
         his.Sumw2()
         f = ds.getFile(syst, iso)
         tdir = f.Get("trees")
         mytree = tdir.Get("Events")
         mytree.Project(his_name, var.name, weight,"same")
         if group.isMC():
            his.Scale(ds.scaleToData(getDataLumi(iso)))
            #print his.Integral()
         else:
            #print group, ds.preScale()
            his.Scale(ds.preScale())
         h.Add(his)
         group.addHistogram(h, var, syst, iso, extra)
