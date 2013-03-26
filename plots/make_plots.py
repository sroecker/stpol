import ROOT
from project_histos import Histogram, MetaData, Cuts, filter_alnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as dict
from common.colors import sample_colors_same as sample_colors

import pdb

def get_max_bin(hists):
    return max([h.GetMaximum() for h in hists])

class ColorStyleGen:
    import itertools
    col_index = 0
    style_index = 0

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta, ROOT.kViolet, ROOT.kSpring]
    styles = [1001, 3005, 3006]
    
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


def legend(hists, pos="top-right", **kwargs):
    """
        hists - list of Histogram type objects
        returns - instance to TLegend
    """
    text_size = kwargs["text_size"] if "text_size" in kwargs.keys() else 0.03
    width = kwargs["width"] if "width" in kwargs.keys() else 0.3
    styles = kwargs.get("styles", len(hists)*["f"])
    if len(styles)<len(hists):
        styles += [styles[-1]]*(len(hists)-len(styles))
    if len(styles) != len(hists):
        raise ValueError("styles must have the sme number of objects as hists")
    styles.reverse()
    
    if pos=="top-right":
        leg_coords = [0.73, 0.61, 0.88, 0.88]
    elif pos=="top-left":
        leg_coords = [0.1, 0.62, 0.26, 0.89]

    leg = ROOT.TLegend(*leg_coords)
    
    for hist in hists:
        leg_style = styles.pop()
        leg.AddEntry(hist.hist, hist.pretty_name, leg_style)
        
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
    import uuid
    stacks = dict()
    styles = kwargs.get("styles")
    draw_styles = kwargs.get("draw_styles", {})
    do_log_y = kwargs.get("do_log_y", False)
    title = kwargs.get("title", "TITLE")
    x_label = kwargs.get("x_label", "XLABEL")
    name = kwargs.get("name", "NAME_%s" % uuid.uuid1())

    canv = ROOT.TCanvas(name, name)
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
    
    max_bin = get_max_bin(stacks.values())
    for name, stack in stacks.items():
        stack.Draw()
    canv.Draw()
 
    first = True
    for name, stack in stacks.items():
        if name in draw_styles.keys():
            drawcmd = draw_styles[name]
        else:
            drawcmd = "BAR HIST "
        if not first:
            drawcmd += " SAME"
        stack.Draw(drawcmd)
        if first:
            stack.SetMaximum(1.5*max_bin)
            stack.SetTitle(title)
            stack.GetXaxis().SetTitle(x_label)

        first = False
    if do_log_y:
        canv.SetLogy()
    return canv, stacks

class Styling:

    def mc_style(hist):
        print "MC style on histogram %s" % hist.name
        color = sample_colors[hist.sample_name]
        hist.hist.SetLineColor(color)
        hist.hist.SetLineWidth(2)
        hist.hist.SetFillColor(color)
        hist.hist.SetFillStyle(1001)

    def data_style(hist):
        hist.hist.SetMarkerStyle(20)
        hist.hist.SetMarkerColor(ROOT.kBlack)
        hist.hist.SetFillStyle(4001)

    style = dict()
    style["mc"] = mc_style
    style["data"] = data_style

def lumi_textbox(lumi=10.435, pos="top-center"):
    if pos=="top-center":
        coords = [0.25, 0.73, 0.71, 0.88]
    text = ROOT.TPaveText(coords[0], coords[1], coords[2], coords[3], "NDC")
    text.AddText("CMS preliminary #sqrt{s} = 8 TeV, #int L dt = %.1f fb^{-1}" % (float(lumi)/1000.0))
    text.SetShadowColor(ROOT.kWhite)
    text.SetLineColor(ROOT.kWhite)
    text.SetFillColor(ROOT.kWhite)
    text.Draw()
    return text

if __name__=="__main__":
    metadata = MetaData("histos.db")

    #cut = Cuts.rms_lj*Cuts.n_jets(3)*Cuts.n_tags(2)
    #weight = "b_weight_nominal"
    #weight = None
    mc_sample_names = [
        "T_s", "Tbar_s",
        "T_tW", "Tbar_tW",
        "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
        "TTJets_FullLept", "TTJets_SemiLept",
        "T_t", "Tbar_t",
    ]
    mc_sample_titles = dict()
    mc_sample_titles["T_t"] = "t-channel (t)"
    mc_sample_titles["Tbar_t"] = "t-channel (#bar{t})"
    mc_sample_titles["T_s"] = "s-channel (t)"
    mc_sample_titles["Tbar_s"] = "s-channel (#bar{t})"
    mc_sample_titles["T_tW"] = "tW-channel (t)"
    mc_sample_titles["Tbar_tW"] = "tW-channel (#bar{t})"
    mc_sample_titles["W1Jets_exclusive"] = "W+jets (excl)"
    mc_sample_titles["W2Jets_exclusive"] = "W+jets (excl)"
    mc_sample_titles["W3Jets_exclusive"] = "W+jets (excl)"
    mc_sample_titles["W4Jets_exclusive"] = "W+jets (excl)"
    mc_sample_titles["TTJets_MassiveBinDECAY"] = "t#bar{t}"
    mc_sample_titles["TTJets_FullLept"] = "t#bar{t} (excl)"
    mc_sample_titles["TTJets_SemiLept"] = "t#bar{t} (excl)"
    
    
    data_sample_names = ["SingleMuD_7274_pb"]
    def stack_plot(var, cut, weight=None, **kwargs):

        hists_mc = [metadata.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=weight) for sample_name in mc_sample_names]
        hists_d = dict()
        for hist in hists_mc:
            hists_d[hist.sample_name] = hist
        
        for hist in hists_mc:
            if hist.sample_name in mc_sample_titles.keys():
                hist.pretty_name = mc_sample_titles[hist.sample_name]
            else:
                hist.pretty_name = hist.sample_name
    
        data_sample_names = ["SingleMuD_7274_pb"]
        hists_data = [metadata.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=None) for sample_name in data_sample_names]
        
        for hist in hists_data:
            hist.pretty_name = "SingleMu"
            
        stack_group = dict()
        stack_group["mc"] = hists_mc
        stack_group["data"] = hists_data
        for hist in stack_group["mc"]:
            hist.normalize_lumi(7274)
    

        canv, stacks = plot_hists_stacked(stack_group, styles=Styling.style, draw_styles={"data": "E1"}, **kwargs)
        #canvas_margin(canv, side="R", margin=0.3)
        leg_hists = [hists_data[0]] + [hists_d["T_t"]] + [hists_d["TTJets_FullLept"]] + [hists_d["W3Jets_exclusive"]]  + [hists_d["T_tW"]] + [hists_d["T_s"]]
        leg = legend(leg_hists, styles=["p", "f"])
        text = lumi_textbox(lumi=7274)
        canv.SaveAs(canv.GetName() + ".pdf")
        return canv, stacks, leg, hists_mc, hists_data, text

#    ret1 = stack_plot("n_tags", Cuts.mt_mu*Cuts.n_jets(2),
#        weight="pu_weight",
#        name="n_tags_plot_2J1T",
#        title="N_{tags} in mu, 2J, PUw."
#    )
#    
    
    ret3 = stack_plot("top_mass", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj,
        name="top_mass_plot_2J1T",
        title="M_{bl#nu} in mu, M_{t}(W)>50 GeV, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5",
        x_label="M_{bl#nu} [GeV]"
    )
    
    ret4 = stack_plot("cos_theta", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
        name="cos_theta_plot_2J1T",
        title="cos #theta_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV",
        x_label="cos #theta_{lj}"
    )

    ret4_1 = stack_plot("cos_theta", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
        weight="pu_weight",
        name="cos_theta_plot_2J1T_pu_weight",
        title="cos #theta_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV, PUw.",
        x_label="cos #theta_{lj}"
    )

    n_jets = [2,3]
    n_tags = [0,1,2]
    weights = [None, "pu_weight"]
    rets = []
    for nj, nt, weight in itertools.product(n_jets, n_tags, weights):
        ret = stack_plot("eta_lj", Cuts.mt_mu*Cuts.n_jets(nj)*Cuts.n_tags(nt),
            weight=weight,
            name="eta_lj_%dJ%dT_" % (nj, nt, weight),
            title="#eta_{lj} in mu, M_{t}(W)>50 GeV, %dJ%dT %s" % (nj, nt, weight),
            x_label="#eta_{lj}"
        )
        rets.append(ret)

    ret2 = stack_plot("eta_lj", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1),
        weight="pu_weight",
        name="eta_lj_plot_2J1T",
        title="#eta_{lj} in mu, 2J1T, PUw."
    )

    ret6 = stack_plot("eta_lj", Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(0),
        weight="pu_weight",
        name="eta_lj_3J0T",
        title="#eta_{lj} in mu, M_{t}(W)>50, 3J0T, PUw",
        x_label="#eta_{lj}"
    )
    ret7 = stack_plot("eta_lj", Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(1),
        weight="pu_weight",
        name="eta_lj_3J1T",
        title="#eta_{lj} in mu, M_{t}(W)>50 GeV, 3J1T, PUw",
        x_label="#eta_{lj}"
    )
    ret8 = stack_plot("eta_lj", Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(2),
        weight="pu_weight",
        name="eta_lj_3J2T",
        title="#eta_{lj} in mu, M_{t}(W)>50 GeV, 3J2T, PUw",
        x_label="#eta_{lj}"
    )

    ret9 = stack_plot("eta_lj", Cuts.mt_mu*Cuts.rms_lj*Cuts.n_jets(3)*Cuts.n_tags(2),
        weight="pu_weight",
        name="eta_lj_3J2T_rms_lj",
        title="#eta_{lj} in mu, M_{t}(W)>50 GeV, 3J2T, RMS_{lj}<0.025, PUw",
        x_label="#eta_{lj}"
    )
    #canv.SaveAs("eta_lj.pdf")
