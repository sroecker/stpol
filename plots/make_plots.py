import ROOT
from project_histos import Histogram, MetaData, Cuts, filter_alnum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from collections import OrderedDict as dict
from common.colors import sample_colors_same as sample_colors
import itertools

import pdb

def get_max_bin(hists):
    return max([h.GetMaximum() for h in hists])

class ColorStyleGen:
    import itertools
    col_index = 0
    style_index = 0

    colors = [ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta, ROOT.kYellow, ROOT.kBlack]
    styles = [1001]#, 3005, 3006]

    colstyles = itertools.product(colors, styles)

    @staticmethod
    def next():
        return ColorStyleGen.colstyles.next()
    
    
    @staticmethod
    def reset():
        ColorStyleGen.colstyles = itertools.product(ColorStyleGen.colors, ColorStyleGen.styles)


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
    if pos=="top-right-small":
        leg_coords = [0.70, 0.77, 0.78, 0.88]
    elif pos=="top-left":
        leg_coords = [0.1, 0.62, 0.26, 0.89]
    elif pos=="bottom-center":
        leg_coords = [0.53, 0.12, 0.58, 0.39]

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
    draw_cmd = kwargs["draw_cmd"] if "draw_cmd" in kwargs.keys() else "E1"
    title = kwargs["title"] if "title" in kwargs.keys() else "NOTITLE"
    line_width = kwargs["line_width"] if "line_width" in kwargs.keys() else 2
    x_label = kwargs.get("x_label", "XLABEL")
    y_label = kwargs.get("y_label", "events/bin")
    do_log_y = kwargs["do_log_y"] if "do_log_y" in kwargs.keys() else False
    min_bin = kwargs.get("min_bin", 0)
    styles = kwargs.get("styles", {})
    if do_normalized:
        for h in hists:
            h.normalize()

    max_bin = get_max_bin([hist.hist for hist in hists])

    first = False
    for hist in hists:
        hist.hist.Draw(draw_cmd + (" SAME" if first else ""))
        first = True
        if hist.name not in styles.keys():
            (color, style) = ColorStyleGen.next()
            hist.hist.SetLineColor(color)
            hist.hist.SetLineWidth(line_width)
            hist.hist.SetFillColor(color)
            hist.hist.SetFillStyle(style)
        else:
            styles[hist.name](hist)

    hists[0].hist.SetTitle(title)
    hists[0].hist.SetStats(False)
    hists[0].hist.SetMaximum(1.5*max_bin)
    hists[0].hist.SetMinimum(min_bin)
    hists[0].hist.GetXaxis().SetTitle(x_label)
    hists[0].hist.GetYaxis().SetTitle(y_label)

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
    min_bin = kwargs.get("min_bin", 10)

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
            drawcmd = "BAR HIST goff"
        if not first:
            drawcmd += " SAME"
        stack.Draw(drawcmd)
        if first:
            stack.SetMaximum(1.8*max_bin)
            if do_log_y:
                stack.SetMinimum(min_bin)
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

def merge_hists_g(hists_d, merge_groups):
    out_d = dict()
    for merge_name, items in merge_groups.items():
        hist = hists_d[items[0]].hist.Clone()
        for item in items[1:]:
            hist.Add(hists_d[item].hist)
        
        out_d[merge_name] = Histogram()
        out_d[merge_name].setHist(hist, sample_name=hists_d[items[0]].sample_name, var=hists_d[items[0]].var, cut=hists_d[items[0]].cut)
        integral, err = out_d[merge_name].calc_int_err()
        out_d[merge_name].pretty_name = "%s : %.0f #pm %0.f" % (merge_name, integral, err)
    return out_d

def merge_hists(hists, name):
    outh = Histogram()
    ROOT.gROOT.cd()
    merged_hist = hists[0].hist.Clone(name)
    for hist in hists[1:]:
        merged_hist.Add(hist.hist)
    outh.setHist(merged_hist)
    return outh

if __name__=="__main__":
    metadata_iso = MetaData("histos_iso.db")
    metadata_antiiso = MetaData("histos_anti-iso.db")

    #cut = Cuts.rms_lj*Cuts.n_jets(3)*Cuts.n_tags(2)
    #weight = "b_weight_nominal"
    #weight = None
    mc_sample_names = [
        "T_s", "Tbar_s",
        "T_tW", "Tbar_tW",
        "WW", "ZZ", "WZ",
        "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
        #"WJets_inclusive",
        "TTJets_FullLept", "TTJets_SemiLept",
        "T_t", "Tbar_t",
        "DYJets"
    ]
    qcd_sample_names = ["QCDMu"]
    mc_sample_titles = dict()
    mc_sample_titles["T_t"] = "t-channel"
    #mc_sample_titles["Tbar_t"] = "t-channel (#bar{t})"
    mc_sample_titles["T_s"] = "s-channel"
    #mc_sample_titles["Tbar_s"] = "s-channel (#bar{t})"
    mc_sample_titles["T_tW"] = "tW-channel"
    #mc_sample_titles["Tbar_tW"] = "tW-channel (#bar{t})"
    mc_sample_titles["W1Jets_exclusive"] = "W+jets"
    mc_sample_titles["WJets_inclusive"] = "W+jets"
    #mc_sample_titles["W2Jets_exclusive"] = "W+jets (excl)"
    #mc_sample_titles["W3Jets_exclusive"] = "W+jets (excl)"
    #mc_sample_titles["W4Jets_exclusive"] = "W+jets (excl)"
    #mc_sample_titles["TTJets_MassiveBinDECAY"] = "t#bar{t}"
    mc_sample_titles["TTJets_FullLept"] = "t#bar{t}"
    #mc_sample_titles["TTJets_SemiLept"] = "t#bar{t} (excl)"
    mc_sample_titles["WW"] = "diboson"
    mc_sample_titles["QCDMu"] = "QCD (MC)"


    data_sample_names = ["SingleMuAB", "SingleMuC", "SingleMuD"]
    lumi_total = 5306+6781+7274
    def stack_plot(var, cut, weight=None, **kwargs):
        qcd_weight = kwargs.get("qcd_weight", None)
        skip_samples = kwargs.get("skip_samples", [])
        hists_mc = [metadata_iso.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=weight) for sample_name in mc_sample_names]
        
        hists_qcd_iso = [metadata_iso.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=qcd_weight) for sample_name in qcd_sample_names]
        hists_data_antiiso = [metadata_antiiso.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=None) for sample_name in data_sample_names]
        
        hists_d = dict()
        for hist in hists_mc:
            hists_d[hist.sample_name] = hist

#        for hist in hists_mc:
#            if hist.sample_name in mc_sample_titles.keys():
#                hist.pretty_name = mc_sample_titles[hist.sample_name]
#            else:
#                hist.pretty_name = hist.sample_name

        hists_data = [metadata_iso.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=None) for sample_name in data_sample_names]
        for hist in hists_data:
            hists_d[hist.sample_name] = hist
            
        for hist in hists_data:
            hist.pretty_name = "SingleMu"

        stack_group = dict()
        stack_group["mc"] = hists_mc
        #stack_group["data"] = hists_data
        stack_group["data"] = [hists_data[0]]
        for hist in stack_group["mc"]:
            hist.normalize_lumi(lumi_total)
        for hist in hists_qcd_iso:
            hist.normalize_lumi(lumi_total)
    
        merge_cmd = dict()
        merge_cmd["data"] = ["SingleMuAB", "SingleMuC", "SingleMuD"]
        merge_cmd["diboson"] = ["WW", "WZ", "ZZ"]
        merge_cmd["DY-jets"] = ["DYJets"]
        merge_cmd["s-channel"] = ["T_s", "Tbar_s"]
        merge_cmd["tW-channel"] = ["T_tW", "Tbar_tW"]
        merge_cmd["t#bar{t}"] = ["TTJets_FullLept", "TTJets_SemiLept"]
        merge_cmd["W+jets"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
        #merge_cmd["W+jets"] = ["WJets_inclusive"]
        merge_cmd["t-channel"] = ["T_t", "Tbar_t"]
        #merge_cmd["QCD (MC)"] = ["QCDMu"]

        for sample in skip_samples:
            if sample in merge_cmd.keys():
                merge_cmd.pop(sample)
        
        merged_hists = merge_hists_g(hists_d, merge_cmd)
        hist_data_antiiso = merge_hists(hists_data_antiiso, "data_antiiso")
        hist_qcd_iso = merge_hists(hists_qcd_iso, "qcd_iso")
        hist_data_antiiso.normalize(hist_qcd_iso.hist.Integral())
        print hist_data_antiiso.hist.Integral()
        hist_data_antiiso.sample_name = "QCDMu"
        hist_data_antiiso.pretty_name = "QCD (dd.)"
        for hist in hists_data[1:]:
            stack_group["data"][0].hist.Add(hist.hist)

        stack_d = dict()
        stack_d["mc"] = [hist_data_antiiso] + [merged_hists[name] for name in merged_hists.keys() if name!="data"]
        stack_d["data"] = [merged_hists["data"]]
        canv, stacks = plot_hists_stacked(
            stack_d,
            styles=Styling.style, draw_styles={"data": "E1"}, **kwargs
        )
        #canvas_margin(canv, side="R", margin=0.3)
#        leg_hists = ([hists_data[0]] +
#            [hists_d["T_t"]] +
#            [hists_d["TTJets_FullLept"]] +
#            [hists_d["W1Jets_exclusive"]]  +
#            [hists_d["T_tW"]] +
#            [hists_d["T_s"]]  +
#            [hists_d["WW"]] +
#            [hists_d["QCDMu"]])
        stack_d["mc"].reverse()
        leg = legend(stack_d["data"] + stack_d["mc"], styles=["p", "f"])
        text = lumi_textbox(lumi=lumi_total)
        canv.SaveAs(canv.GetName() + ".pdf")
#        return hists_d
#        return canv, stacks, leg, hists_mc, hists_data, text


    doStacks = True
    if doStacks:
        ret00 = stack_plot("mt_mu", Cuts.no_cut,
            #weight="pu_weight",
            name="met_plot",
            title="M_{t}(W) in mu",
            do_log_y=False,
            x_label="M_{t}(W) [GeV]",
            weight="pu_weight"
        )
        
        
        ret0 = stack_plot("n_jets", Cuts.mt_mu,
            #weight="pu_weight",
            name="n_jets_plot_log",
            title="N_{jets} in mu, PUw.",
            do_log_y=True,
            x_label="N_{jets}",
            min_bin=1000,
            weight="pu_weight"
        )

        ret1 = stack_plot("n_tags", Cuts.mt_mu*Cuts.n_jets(2),
            #weight="pu_weight",
            name="n_tags_plot_2J_log",
            title="N_{tags} in mu, 2J, PUw.",
            do_log_y=True,
            x_label="N_{tags}",
            min_bin=1000,
            weight="pu_weight"

        )

        ret2 = stack_plot("n_tags", Cuts.mt_mu*Cuts.n_jets(3),
            #weight="pu_weight",
            name="n_tags_plot_3J_log",
            title="N_{tags} in mu, 3J, PUw.",
            do_log_y=True,
            x_label="N_{tags}",
            min_bin=1000,
            weight="pu_weight"
        )
        
        ret0 = stack_plot("n_jets", Cuts.mt_mu,
            #weight="pu_weight",
            name="n_jets_plot",
            title="N_{jets} in mu, PUw.",
            do_log_y=False,
            x_label="N_{jets}",
            weight="pu_weight"
        )

        ret1 = stack_plot("n_tags", Cuts.mt_mu*Cuts.n_jets(2),
            #weight="pu_weight",
            name="n_tags_plot_2J",
            title="N_{tags} in mu, 2J, PUw.",
            do_log_y=False,
            x_label="N_{tags}",
            weight="pu_weight"
        )

        ret2 = stack_plot("n_tags", Cuts.mt_mu*Cuts.n_jets(3),
            #weight="pu_weight",
            name="n_tags_plot_3J",
            title="N_{tags} in mu, 3J, PUw.",
            do_log_y=False,
            x_label="N_{tags}",
            weight="pu_weight"
        )


        ret3 = stack_plot("top_mass", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj,
            name="top_mass_plot_2J1T",
            title="M_{bl#nu} in mu, M_{t}(W)>50 GeV, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, PUw., Bw.",
            x_label="M_{bl#nu} [GeV]",
            #skip_samples=["QCD (MC)"],
            weight="pu_weight*b_weight_nominal"
        )

        ret4 = stack_plot("cos_theta", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            name="cos_theta_plot_2J1T",
            title="cos #theta_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV",
            x_label="cos #theta_{lj}",
            #skip_samples=["QCD (MC)"],
            weight="pu_weight"
        )

        ret4_1 = stack_plot("cos_theta", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            weight="pu_weight",
            name="cos_theta_plot_2J1T_pu_weight",
            title="cos #theta_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV, PUw.",
            x_label="cos #theta_{lj}",
            #skip_samples=["QCD (MC)"]
        )

        ret4_2 = stack_plot("cos_theta", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            weight="pu_weight*b_weight_nominal",
            name="cos_theta_plot_2J1T_pu_weight_b_weight",
            title="cos #theta_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV, PUw., Bw.",
            x_label="cos #theta_{lj}",
            skip_samples=["QCD (MC)"]
        )

        n_jets = [2,3]
        n_tags = [0,1,2]
        weights = [None, "pu_weight", "pu_weight*b_weight_nominal"]
        rets = []
        for nj, nt, weight in itertools.product(n_jets, n_tags, weights):
            def title(nj, nt, weight):
                ret = "#eta_{lj} in mu, M_{t}(W)>50 GeV, %dJ%dT" % (nj, nt)
                if weight=="pu_weight":
                    ret += ", PUw."
                return ret
            ret = stack_plot("eta_lj", Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(nj)*Cuts.n_tags(nt),
                weight=weight,
                name="eta_lj_%dJ%dT_%s" % (nj, nt, weight),
                title=title(nj, nt, weight),
                x_label="#eta_{lj}"
            )
            rets.append(ret)

        ret5 = stack_plot("n_vertices", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            weight="pu_weight",
            name="n_vertices_2J1T_pu_weighted",
            title="N_{vtx.} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV, PUw.",
            x_label="N_{vtx.}"
        )
        ret5_1 = stack_plot("n_vertices", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            #weight="pu_weight",
            name="n_vertices_2J1T_unweighted",
            title="N_{vtx.} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV",
            x_label="N_{vtx.}"
        )

        ret6 = stack_plot("rms_lj", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
            #weight="pu_weight",
            name="rms_lj_2J1T_puw",
            title="RMS_{lj} in mu, M_{t}(W)>50 GeV, 2J1T, #eta_{lj}>2.5, M_{bl#nu} #in [130, 220] GeV",
            x_label="RMS_{lj}",
            do_log_y=True,
            #weight="pu_weight",
        )

        ret6_1 = stack_plot("rms_lj", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0),
            #weight="pu_weight",
            name="rms_lj_2J0T_puw",
            title="RMS_{lj} in mu, M_{t}(W)>50 GeV, 2J0T",
            x_label="RMS_{lj}",
            do_log_y=False,
            weight="pu_weight",
            qcd_weight="pu_weight",
        )


        ret6_2 = stack_plot("rms_lj", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1),
            #weight="pu_weight",
            name="rms_lj_2J1T_puw",
            title="RMS_{lj} in mu, M_{t}(W)>50 GeV, 2J1T",
            x_label="RMS_{lj}",
            do_log_y=False,
            weight="pu_weight",
            qcd_weight="pu_weight",
        )


        ret6_1 = stack_plot("rms_lj", Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(0),
            #weight="pu_weight",
            name="rms_lj_3J0T_puw",
            title="RMS_{lj} in mu, M_{t}(W)>50 GeV, 3J0T",
            x_label="RMS_{lj}",
            do_log_y=False,
            weight="pu_weight",
            qcd_weight="pu_weight",
        )


        ret6_1 = stack_plot("rms_lj", Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(1),
            #weight="pu_weight",
            name="rms_lj_3J1T_puw",
            title="RMS_{lj} in mu, M_{t}(W)>50 GeV, 3J1T",
            x_label="RMS_{lj}",
            do_log_y=False,
            weight="pu_weight",
            qcd_weight="pu_weight",
        )
    total_lumi = 5306+6781+7274
    def data_mc_ratio(ratio_groups, var, cut, **kwargs):
        ColorStyleGen.reset()
        samples_mc = ratio_groups.keys()
        ratio_groups["data"] = ["SingleMuAB", "SingleMuC", "SingleMuD"]
        plot_name = kwargs.get("name", "plot")
        samples_d = dict()
        for name, group in ratio_groups.items():
            samples_d[name] = [
                metadata_iso.get_histogram(sample_name, var, cut_str=cut.cut_str, weight=None) for
                sample_name in group
            ]

            if name != "data":
                for hist in samples_d[name]:
                    hist.normalize_lumi(total_lumi)
            merged = merge_hists(samples_d[name], name)
            samples_d[name] = merged
            samples_d[name].pretty_name = name

        for name in samples_d.keys():
            if name != "data":
                samples_d[name].hist.Divide(samples_d["data"].hist)
        samples_d["data"].hist.Divide(samples_d["data"].hist)
    
        canv = plot_hists(
            samples_d.values(),
            styles={"data": Styling.style["data"]},
            **kwargs
        )
        leg = legend([r for r in reversed(samples_d.values())], styles=["p", "f"])
        canv.SaveAs(plot_name + ".pdf")
        return canv, leg

    doRatio=False

    if doRatio:
        ratio_d = dict()
        ratio_d["W+jets excl."] = ["WJets_inclusive"]
        ratio_d["W+jets incl."] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
        ratio_d["mc (W+jets incl.)"] = [
            "T_s", "Tbar_s",
            "T_tW", "Tbar_tW",
            "WW", "ZZ", "WZ",
            "WJets_inclusive",
            "TTJets_FullLept", "TTJets_SemiLept",
            "T_t", "Tbar_t",
            "DYJets",
            "QCDMu"
        ]
        ratio_d["mc (W+jets excl.)"] = [
            "T_s", "Tbar_s",
            "T_tW", "Tbar_tW",
            "WW", "ZZ", "WZ",
            "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
            "TTJets_FullLept", "TTJets_SemiLept",
            "T_t", "Tbar_t",
            "DYJets",
            "QCDMu"
        ]
        ret1 = data_mc_ratio(ratio_d, "n_jets", Cuts.mt_mu, name="ratio_n_jets", title="MC/data ratio in N_{jets}, M_t(W) > 50GeV")
        
        ratio_d = dict()
        ratio_d["t#bar{t} incl."] = ["TTJets_MassiveBinDECAY"]
        ratio_d["t#bar{t} excl."] = ["TTJets_SemiLept", "TTJets_FullLept"]
        ratio_d["mc (t#bar{t} incl.)"] = [
            "T_s", "Tbar_s",
            "T_tW", "Tbar_tW",
            "WW", "ZZ", "WZ",
            "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
            "TTJets_MassiveBinDECAY",
            #"TTJets_FullLept", "TTJets_SemiLept",
            "T_t", "Tbar_t",
            "DYJets",
            "QCDMu",
        ]
        ratio_d["mc (t#bar{t} excl.)"] = [
            "T_s", "Tbar_s",
            "T_tW", "Tbar_tW",
            "WW", "ZZ", "WZ",
            "W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive",
            "TTJets_FullLept", "TTJets_SemiLept",
            "T_t", "Tbar_t",
            "DYJets",
            "QCDMu"
        ]
        ret2 = data_mc_ratio(ratio_d, "eta_lj", Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(2),
            name="ratio_eta_lj_3J2T",
            title="MC/data ratio in 3J2T, rms_{lj} < 0.025, M_{t}(W) > 50 GeV",
            x_label="#eta_{lj}",
            y_label="MC/data ratio"
        )

    cut = Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig
    hist_qcd_mc = metadata_iso.get_histogram("QCDMu", "cos_theta",
        cut_str=cut.cut_str, weight=None
    )
    hist_qcd_data = metadata_antiiso.get_histogram("SingleMuD", "cos_theta",
        cut_str=cut.cut_str, weight=None
    )
    print hist_qcd_mc.hist.Integral()
    hist_qcd_data.normalize(hist_qcd_mc.hist.Integral())
    hists_to_plot = [hist_qcd_mc, hist_qcd_data]
    ret = plot_hists(hists_to_plot)
    leg = legend(hists_to_plot)
    