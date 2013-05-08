import sys
import os

#Need to add parent dir to python path to import plots
try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, did you run `source setenv.sh` in the code base directory?"
    sys.exit(1)

import tdrstyle
tdrstyle.tdrstyle()

import ROOT
from plots.common.sample_style import Styling
from plot_defs import hist_def
from plots.common.utils import lumi_textbox
from plots.common.legend import legend
from plots.common.pretty_names import variable_names

from file_names import dataLumi
Lumi = sum(dataLumi.values())

mode = "final"
#mode = "2j1t_nomet"

apply_PUw = True
apply_Bw = True
apply_Elw = True

weight = ""
if  apply_PUw:
    weight += "_PUw"
if apply_Bw:
    weight += "_Bw"
if apply_Elw:
    weight += "_Elw_ElTrw"
    
filename = mode + weight + ".root"
histograms = "Histograms/" + mode + "/" + filename
print "Opening input file: " + histograms
h = ROOT.TFile(histograms)

from plots.common.utils import merge_cmds
process_names = merge_cmds.keys()
process_names.insert(1,"QCD")

for hist_name in hist_def:
    hist_to_plot = hist_def[hist_name][0]
    print "Plotting:" + hist_to_plot

    from plots.common.odict import OrderedDict as dict
    mc_to_plot = dict()

    mc_to_plot["diboson"] = h.Get("diboson/" + hist_to_plot)
    mc_to_plot["WJets_inclusive"] = h.Get("wjets/" + hist_to_plot)
    mc_to_plot["DYJets"] = h.Get("zjets/" + hist_to_plot)
    mc_to_plot["TTJets"] = h.Get("ttjets/" + hist_to_plot)
    mc_to_plot["T_tW"] = h.Get("tW/" + hist_to_plot)
    mc_to_plot["T_s"] = h.Get("sch/" + hist_to_plot)
    mc_to_plot["signal"] = h.Get("signal/" + hist_to_plot)

    if hist_name == "cos_theta" or hist_name == "eta_lj":
        nrebin = 4
    elif hist_name == "met" or hist_name == "el_pt" or hist_name == "top_mass":
        nrebin = 2
    else:
        nrebin =1    
    
    data = h.Get("data/" + hist_to_plot)

    qcd = h.Get("data_anti/" + hist_to_plot)
    
    if mode == "final": 
        qcd_norm = 1103.55*84./1808
    if mode == "2j0t_nomet":
        qcd_norm = 38990
    if mode == "2j1t_nomet":
        qcd_norm = 982.7
    qcd.Scale(qcd_norm/qcd.Integral()) #rescale qcd template according to the best-fit value

#--------------Rebin----------------
    for key in mc_to_plot:
        mc_to_plot[key].Rebin(nrebin)
        Styling.mc_style(mc_to_plot[key],key)

    qcd.Rebin(nrebin)
    Styling.mc_style(qcd,"QCD")

    data.Rebin(nrebin)
    Styling.data_style(data)

#--------------stack----------------------------
    sum = ROOT.THStack("sum","")
    h_sumMC = mc_to_plot["signal"].Clone("h_sumMC")

    for key in mc_to_plot:
        if key != "signal":
            h_sumMC.Add(mc_to_plot[key])
    h_sumMC.Add(qcd)

    sum.Add(qcd)
    for sample in mc_to_plot.values():
        sum.Add( sample )

#-------------------style------------------------
    h_sumMC.SetTitle("")
    h_sumMC.SetStats(False)
    h_sumMC.SetLineWidth(2)
    h_sumMC.SetMaximum(  1.3*max( h_sumMC.GetMaximum(), data.GetMaximum() ))
    h_sumMC.SetLineColor(ROOT.kBlack)
    h_sumMC.SetFillStyle(0)
    h_sumMC.GetXaxis().SetTitle(variable_names[hist_name]);    
#---------------------Draw----------------------------
    c = ROOT.TCanvas("c","")
    h_sumMC.Draw("hist")
    sum.Draw("histsame")
    h_sumMC.Draw("histsame")
    data.Draw("epsame")
#--------------- lumi box and legend-----------------
    if hist_name == "cos_theta" or hist_name == "eta_lj":
        legend_pos = "top-left"
    else:
        legend_pos = "top-right"

    if legend_pos == "top-right":
        lumibox = lumi_textbox(Lumi,"top-left")
    if legend_pos == "top-left":
        lumibox = lumi_textbox(Lumi,"top-right")
    
    hist_list = mc_to_plot.values()
    hist_list.reverse() # reverse order of mc histograms for the legend entry
    hist_list.append(qcd)
    hist_list.insert(0,data)
    
    leg = legend(
        hist_list,
        names = process_names,
        styles=["p", "f"],
        width=0.25,
        pos = legend_pos
        )

    outfilename = "Plots/" + mode + "/" + hist_to_plot + weight + ".pdf"
    c.SaveAs(outfilename)
    c.Close()
 #------------------------------print cut flow--------------------------
print("CUT FLOW:")
print("signal: "+ str(mc_to_plot["signal"].Integral()) + " +- " + str( mc_to_plot["signal"].Integral()/(mc_to_plot["signal"].GetEntries()**0.5) ) )
print("ttbar: " + str(mc_to_plot["TTJets"].Integral()) + " +- " + str( mc_to_plot["TTJets"].Integral()/(mc_to_plot["TTJets"].GetEntries()**0.5) ) ) 
print("W + jets: " + str(mc_to_plot["WJets_inclusive"].Integral()) + " +- " + str( mc_to_plot["WJets_inclusive"].Integral()/(mc_to_plot["WJets_inclusive"].GetEntries()**0.5) ) )
print("Z + jets: " + str(mc_to_plot["DYJets"].Integral()) + " +- " + str( mc_to_plot["DYJets"].Integral()/(mc_to_plot["DYJets"].GetEntries()**0.5) ) )
print("stop: " + str(mc_to_plot["T_s"].Integral()) + " +- " + str( mc_to_plot["T_s"].Integral()/(mc_to_plot["T_s"].GetEntries()**0.5) ) )
print("diboson: " + str(mc_to_plot["diboson"].Integral()) + " +- " + str( mc_to_plot["diboson"].Integral()/(mc_to_plot["diboson"].GetEntries()**0.5) ) )
print("QCD: " + str(qcd.Integral()) + " +- " + str( qcd.Integral()/(qcd.GetEntries()**0.5) ) )
#print("----------------------")
print("sum MC: " + str(h_sumMC.Integral()))
print("Data: " + str(data.Integral()) + " +- " + str( data.Integral()**0.5 ) )

