import ROOT
from project_histos import Sample, Cuts
import argparse
from collections import OrderedDict as dict
from make_plots import plot_hists_stacked, Styling, merge_hists_g, g_merge_cmd

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="iso")
    parser.add_argument("-d", "--dir", type=str, default="/Users/joosep/Documents/stpol/data/step3_trees_Apr04")
    lumi_total = 18062
    args = parser.parse_args()
    
    samples_mc = Sample.fromDirectory(args.dir + "/" + args.type + "/mc")
    samples_data = Sample.fromDirectory(args.dir + "/" + args.type + "/data")
    
    def compare_plot(var, plot_range, weight, cut):
        histsD = dict()
        
        for samp in samples_mc:
            histsD[samp.name] = samp.drawHistogram(var, str(cut), weight=weight, plot_range=plot_range)

        for name, hist in histsD.items():
            hist.normalize_lumi(lumi_total)

        for samp in samples_data:
            histsD[samp.name] = samp.drawHistogram(var, str(cut), plot_range=plot_range)


        merge_cmd = g_merge_cmd
        merge_cmd["QCD (MC)"] = ["QCDMu"]
        merged_hists = merge_hists_g(histsD, merge_cmd)

        stack = dict()
        stack["mc"] = [merged_hists[name] for name in merged_hists.keys() if name!="data"]
        stack["data"] = [merged_hists["data"]]


        canv, stacks = plot_hists_stacked(
                stack,
                styles=Styling.style, draw_styles={"data": "E1"},
        )
        return canv, stacks

    cut = Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)
    A = compare_plot("abs(eta_lj)", [10, 0, 5], "1.0", cut)
    B = compare_plot("abs(eta_lj)", [10, 0, 5], "pu_weight", cut)

    
    