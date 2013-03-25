import ROOT
from plots_base import Histogram, MetaData, Cuts
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as dict

import pdb

def get_max_bin(hists):
    return max([h.GetMaximum() for h in hists])

class ColorStyleGen:
    import itertools
    col_index = 0
    style_index = 0

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta]
    styles = [3004]
    
    colstyles = itertools.product(colors, styles)

    @staticmethod
    def next():
        return ColorStyleGen.colstyles.next()

def canvas_margin(canvas, side="R", margin=0.3):
    if side=="R":
        canvas.SetRightMargin(margin)
    if side=="L":
        canvas.SetLeftMargin(margin)
    if side=="B":
        canvas.SetBottomMargin(margin)

def legend(hists, side="R", **kwargs):
    
    text_size = kwargs["text_size"] if "text_size" in kwargs.keys() else 0.03
    width = kwargs["width"] if "width" in kwargs.keys() else 0.3
    if side=="R":
        leg_coords = [1.0-width+0.01, 0.0, 0.99, 0.9]
    leg = ROOT.TLegend(*leg_coords)
    for hist in hists:
        leg.AddEntry(hist, hist.GetName())
    leg.Draw()
    leg.SetFillColor(ROOT.kWhite)
    leg.SetLineColor(ROOT.kWhite)
    leg.SetTextSize(0.03)
    return leg

def plot_hists(hists, name="canv", **kwargs):
    canv = ROOT.TCanvas(name, name)
    do_normalized = kwargs["do_normalized"] if "do_normalized" in kwargs.keys() else False
    draw_cmd = kwargs["draw_cmd"] if "draw_cmd" in kwargs.keys() else "BAR E1"
    title = kwargs["title"] if "title" in kwargs.keys() else "NOTITLE"
    line_width = kwargs["line_width"] if "line_width" in kwargs.keys() else 2
    x_label = kwargs["x_label"] if "x_label" in kwargs.keys() else "NOLABEL"
    do_log_y = kwargs["do_log_y"] if "do_log_y" in kwargs.keys() else False
    if do_normalized:
        for h in hists:
            h.normalize()

    max_bin = get_max_bin([hist.hist for hist in hists])
    
    first = False
    for hist in hists:
        hist.hist.Draw(draw_cmd + (" SAME" if first else ""))
        first = True
        (color, style) = ColorStyleGen.next()
        hist.hist.SetLineColor(color)
        hist.hist.SetLineWidth(line_width)
        hist.hist.SetFillColor(color)
        hist.hist.SetFillStyle(style)

    hists[0].hist.SetTitle(title)
    hists[0].hist.SetStats(False)
    hists[0].hist.SetMaximum(1.5*max_bin)
    hists[0].hist.GetXaxis().SetTitle(x_label)
    
    if do_log_y:
        canv.SetLogy()
        
    return canv

def plot_hists_stacked(hist_groups, **kwargs):
    stacks = dict()
    styles = kwargs["styles"] if "styles" in kwargs else None
    
    canv = ROOT.TCanvas("c", "c")
    for name, group in hist_groups.items():
        stacks[name] = ROOT.THStack(name, name)
        print name
        for hist in group:
            print hist.name
            
            if not styles:
                (color, style) = ColorStyleGen.next()
                hist.hist.SetLineColor(color)
                hist.hist.SetLineWidth(2)
                hist.hist.SetFillColor(color)
                hist.hist.SetFillStyle(style)
            else:
                styles[name](hist)
            stacks[name].Add(hist.hist)
        #stacks[name].Draw("BAR H2 " + ("SAME" if first else ""))
        #first = False
    
    max_bin = get_max_bin(stacks.values())
    for name, stack in stacks.items():
        stack.Draw()
    canv.Draw()
 
    first = True
    for name, stack in stacks.items():
        drawcmd = "BAR H2 " + ("SAME" if not first else "")
        stack.Draw(drawcmd)
        if first:
            stack.SetMaximum(1.5*max_bin)
        first = False
    return canv, stacks

if __name__=="__main__":
    metadata = MetaData("histos.db")

    hists = []

    histsD = dict()
    for hist in metadata.session.query(Histogram).\
                filter(
                    (Histogram.sample_name=="TTJets_FullLept") |
                    (Histogram.sample_name=="SingleMuD_7274_pb") |
                    (Histogram.sample_name=="WJets_inclusive") |
                    (Histogram.sample_name=="T_t")
                ).\
                filter(Histogram.var=="eta_lj").\
                filter(Histogram.cut==Cuts.top_mass).\
                order_by(Histogram.id):
        hist.loadFile()
        hists.append(hist)
        histsD[hist.name] = hist
        print hist

#    canv = plot_hists(hists, name="eta_lj_comparison", title="#eta_{lj} distribution", do_normalized=True)
#    canvas_margin(canv, side="R", margin=0.3)
#    leg = legend([h.hist for h in hists])
#    canv.SaveAs("eta_lj_comparison.pdf")

    print histsD
    mc_keys = ("TTJets_FullLept_eta_lj_top_mass130top_mass220_NOWEIGHT", "T_t_eta_lj_top_mass130top_mass220_NOWEIGHT", "WJets_inclusive_eta_lj_top_mass130top_mass220_NOWEIGHT")
    data_keys = ("SingleMuD_7274_pb_eta_lj_top_mass130top_mass220_NOWEIGHT",)

    stack_group = dict()
    stack_group["data"] = [histsD[k] for k in data_keys]
    stack_group["mc"] = [histsD[k] for k in mc_keys]

    def mc_style(hist):
        (color, style) = ColorStyleGen.next()
        hist.hist.SetLineColor(color)
        hist.hist.SetLineWidth(2)
        hist.hist.SetFillColor(color)
        hist.hist.SetFillStyle(style)

    def data_style(hist):
        hist.hist.SetMarkerStyle(20)
        hist.hist.SetMarkerColor(ROOT.kBlack)
        hist.hist.SetFillStyle(4001)
    styles = dict()
    styles["mc"] = mc_style
    styles["data"] = data_style

    canv, stacks = plot_hists_stacked(stack_group, styles=styles)
    canvas_margin(canv, side="R", margin=0.3)
    leg = legend([h.hist for h in hists])

    #canv = plot_hists_stack({"mc": [histsD[]
    
#                filter(
#                    (Histogram.cut=="n_tags==0.0") |
#                    (Histogram.cut=="n_tags==0.0 && true_b_count==0.0") |
#                    (Histogram.cut=="n_tags==0.0 && true_b_count==1.0") |
#                    (Histogram.cut=="n_tags==0.0 && true_b_count==2.0") |
#                    (Histogram.cut=="n_tags==0.0 && true_b_count==3.0")
#                )


#    first = True
#    colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta]
#    leg = ROOT.TLegend(0.8, 0.3, 0.96, 0.8)
#    leg.SetFillColor(ROOT.kWhite)
#    c = ROOT.TCanvas("c")
#    c.SetLogy()
#    names = ["0_tags", "true_b_0", "true_b_1", "true_b_2", "true_b_3"]
#    titles = ["any number of b-jets", "0 true b-jets", "1 true b-jets", "2 true b-jets", "3 true b-jets"]
#    i = 0
#    for h in hists:
#        h.hist.SetName(names[i])
#        h.hist.SetTitle(titles[i])
#        i += 1
#
#    hists[0].hist.GetXaxis().SetTitle("b-weight (nominal)")
#    hists[0].hist.GetYaxis().SetRangeUser(1, 10**5)
#    for h in hists:
#        color = colors.pop()
#        h.hist.Rebin(2)
#        print "%s: %.2f" % (h.hist.GetName(), h.hist.Integral())
#    #    if(h.hist.Integral()>0):
#    #        h.hist.Scale(1.0/h.hist.Integral())
#        h.hist.SetLineColor(color)
#        h.hist.SetFillColor(color)
#        h.hist.SetFillStyle(3005)
#        if first:
#            h.hist.Draw("H")
#            h.hist.SetStats(False)
#        else:
#            h.hist.Draw("SAME H")
#        leg.AddEntry(h.hist, h.hist.GetTitle())
#        first = False
#        #print (h.hist.Integral()*h.hist.GetMean())
#    leg.Draw()
#    hists[0].hist.SetTitle(sample + " b-weight distributions")
#    #c.SetRightMargin(0.3)
#    c.SaveAs("bWeightDistributions.pdf")
