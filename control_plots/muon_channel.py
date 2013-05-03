#!/usr/bin/env python
#run as ./muon_channel.py -b to skip visual output
import sys
import os

#Need to add parent dir to python path to import plots
sys.path.append(os.environ["STPOL_DIR"] )

import ROOT
import plots
from plots.common.stack_plot import plot_hists_stacked
from plots.common.odict import OrderedDict
import plots.common.pretty_names as pretty_names
import random

if __name__=="__main__":
    import tdrstyle
    tdrstyle.tdrstyle()

    #Make some test data histograms
    h_d1 = ROOT.TH1F("h_d1", "data1", 20, -5, 5)
    for i in range(1000):
        h_d1.Fill(random.normalvariate(0, 1))

    h_d2 = ROOT.TH1F("h_d2", "data2", 20, -5, 5)
    for i in range(10000):
        h_d2.Fill(random.normalvariate(0, 0.8))

    #Merge the different data samples
    h_d1.Add(h_d2)
    h_d1.SetTitle("data")

    #Make some test MC histograms
    #In a real use case, you will retrieve them from the samples
    h_mc1 = ROOT.TH1F("h_mc1", "TTJets", 20, -5, 5)
    h_mc1.SetTitle(pretty_names.sample_names["TTJets_FullLept"])
    for i in range(1500):
        h_mc1.Fill(random.normalvariate(0, 1))

    h_mc2 = ROOT.TH1F("h_mc2", "t-channel", 20, -5, 5)
    for i in range(900):
        h_mc2.Fill(random.normalvariate(0, 0.9))

    h_mc3 = ROOT.TH1F("h_mc3", "W+Jets", 20, -5, 5)
    for i in range(5000):
        h_mc3.Fill(random.normalvariate(0,  1.2))

    #Set the histogram styles and colors
    from plots.common.sample_style import Styling
    Styling.mc_style(h_mc1, "TTJets_FullLept")
    Styling.mc_style(h_mc2, "T_t")
    Styling.mc_style(h_mc3, "W1Jets_exclusive")
    Styling.data_style(h_d1)

    #Create the canvas
    canv = ROOT.TCanvas("c", "c")
    canv.SetWindowSize(500, 500)
    canv.SetCanvasSize(600, 600)

    #!!!!LOOK HERE!!!!!
    #----
    #Draw the stacked histograms
    #----
    stacks_d = OrderedDict() #<<< need to use OrderedDict to have data drawn last (dict does not preserve order)
    stacks_d["mc"] = [h_mc1, h_mc2, h_mc3] # <<< order is important here, mc1 is bottom-most
    stacks_d["data"] = [h_d1]
    stacks = plot_hists_stacked(
        canv,
        stacks_d,
        x_label="variable x [GeV]",
        y_label="",
        do_log_y=False
    )

    #Draw the legend
    from plots.common.legend import legend
    leg = legend(
        [h_d1, h_mc3, h_mc2, h_mc1], # <<< need to reverse MC order here, mc3 is top-most
        styles=["p", "f"],
        width=0.2
    )
    try:
        os.mkdir("muon_out")
    except OSError:
        pass
    canv.SaveAs("muon_out/test.pdf")
