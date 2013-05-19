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

# choose cut region
mode1 = "final"
#mode1 = "2j1t"
#mode1 = "2j0t"

mode1a = ""
#mode1a = "_nomet"

#choose whether inclusive or leptonic ttbar and signal samples are used
#mode2 = "_incl" 
mode2 = "_lep"
mode = mode1 + mode1a + mode2

qcd_from_mc = True
apply_PUw = True
apply_Elw = True
apply_Bw = False

weight = ""
if  apply_PUw:
    weight += "_PUw"
if apply_Bw:
    weight += "_Bw"
if apply_Elw:
    weight += "_Elw_ElTrw"

from plots.common.utils import merge_cmds
process_names = merge_cmds.keys()
process_names.insert(1,"QCD")

#--------------------open file ------------------------
filename = mode1 + mode1a + weight + mode2 +".root"
histograms = "Histograms/" + mode1 + mode1a + "/" + filename
print "Opening input file: " + histograms
h = ROOT.TFile(histograms)

#------------------------------------------------------

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
        
    data = h.Get("data/" + hist_to_plot)
    if qcd_from_mc:
        print "Get QCD from MC"
        qcd = h.Get("qcd_mc/" + hist_to_plot)
    else:
        print "Get QCD from data"
        qcd = h.Get("data_anti/" + hist_to_plot)
        
#----------calculate QCD yield from data--------
    qcd_mode = mode1 + mode2 #omit possible "_nomet" extension as it is always used for the fit
    qcd_norm = 0

    if hist_to_plot != "el_mother_id":
        from qcd_yields import getQCDYield
        qcd_norm = getQCDYield( qcd, qcd_mode, True)
        print "QCD estimated from data = " + str(qcd_norm)

        if qcd.Integral() != 0:
            qcd.Scale(qcd_norm/qcd.Integral()) #rescale qcd template according to the best-fit value

#--------------Rebin----------------
    if hist_name == "cos_theta" or hist_name == "pt_lj" or hist_name == "eta_lj" or hist_name == "el_mva": #<--sometimes need to change rebin to 1, if plots are weird (QCD not shown)
        nrebin = 4
    elif hist_name == "met" or hist_name == "el_pt" or hist_name == "top_mass" or hist_name == "deltaR_lj" or hist_name == "deltaR_bj":
        nrebin = 2
    else:
        nrebin =1

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
    if hist_name == "el_mva":
        h_sumMC.SetMaximum( 5*max( h_sumMC.GetMaximum(), data.GetMaximum() )) 

    h_sumMC.SetLineColor(ROOT.kBlack)
    h_sumMC.SetFillStyle(0)
    h_sumMC.GetXaxis().SetTitle(variable_names[hist_name]);    
#---------------------Draw----------------------------
    c = ROOT.TCanvas("c","")
    if hist_to_plot == "el_mva":
        c.SetLogy()
    h_sumMC.Draw("hist")
    sum.Draw("histsame")
    h_sumMC.Draw("histsame")
    data.Draw("epsame")
#--------------- lumi box and legend-----------------
    if hist_name == "cos_theta" or hist_name == "el_mva":
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

    outfilename = "Plots/" + mode1 + mode1a + "/" + hist_to_plot + mode2 + weight + ".pdf"
    c.SaveAs(outfilename)
    c.Close()

    #----------------Print signal PDG ID information------------------
    if hist_to_plot == "el_mother_id":
        nr_W = mc_to_plot["signal"].GetBinContent(2) + mc_to_plot["signal"].GetBinContent(50)
        nr_tau = mc_to_plot["signal"].GetBinContent(11) + mc_to_plot["signal"].GetBinContent(41)
        print "---------------------------------------"
        print "Electron mother pdgID in signal sample"
        print "nr of prompt electrons from W: " +  str(nr_W )
        print "nr of electrons from tau decays: " + str( nr_tau )
        print "Total: " + str( nr_W + nr_tau)
        print "---------------------------------------"
 #------------------------------print cut flow--------------------------
print("CUT FLOW:")
print("----------------------")
for key in mc_to_plot:
    print key + ": " + str( mc_to_plot[key].Integral() ) + " +- " + str( mc_to_plot[key].Integral()/(mc_to_plot[key].GetEntries()**0.5) )

print("QCD: " + str(qcd.Integral()) + " +- " + str( qcd.Integral()/(qcd.GetEntries()**0.5) ) )
print("----------------------")
print("sum MC: " + str(h_sumMC.Integral()) )
print("Data: " + str(data.Integral()) + " +- " + str( data.Integral()**0.5 ) )
print("----------------------")
print 
print "Electron mother pdgID in signal sample"
print("----------------------")
print "nr of prompt electrons from W: " +  str(nr_W ) + " (" + str(nr_W/mc_to_plot["signal"].Integral()*100) + "%)"
print "nr of electrons from tau decays: " + str( nr_tau ) + " (" + str(nr_tau/mc_to_plot["signal"].Integral()*100) + "%)"
print "Other decays: " + str( mc_to_plot["signal"].Integral() - (nr_W + nr_tau) ) + " (" + str( (mc_to_plot["signal"].Integral() - (nr_W + nr_tau) )/mc_to_plot["signal"].Integral()*100) + "%)"
print "---------------------------------------"
