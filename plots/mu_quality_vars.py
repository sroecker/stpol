import ROOT
ROOT.gROOT.SetBatch(True)
import sys
import os
try:
    sys.path.append(os.environ["STPOL_DIR"] )
except KeyError:
    print "Could not find the STPOL_DIR environment variable, dod you run `source setenv.sh` in the code base directory?"
    sys.exit(1)
from project_histos import Sample, Cuts, Cut
import argparse
from collections import OrderedDict as dict
from common.stack_plot import plot_hists_stacked
from common.utils import merge_hists, merge_cmds
from common.utils import lumi_textbox
from common.legend import legend
from common.sample_style import Styling
import copy

if __name__=="__main__":
    from common.tdrstyle import tdrstyle
    tdrstyle()

    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="iso")
    parser.add_argument("-d", "--dir", type=str, default="/Users/joosep/Documents/stpol/data/05_02/out_step3_05_01_22_36/")
    lumi_total = 19300
    args = parser.parse_args()

    samples_mc = Sample.fromDirectory(args.dir + "/" + args.type + "/mc")
    samples_data = Sample.fromDirectory(args.dir + "/" + args.type + "/data")

    def compare_plot(var, plot_range, weight, cut, **kwargs):
        histsD = dict()

        for samp in samples_mc:
            histsD[samp.name] = samp.drawHistogram(var, str(cut), weight=weight, plot_range=plot_range)
            Styling.mc_style(histsD[samp.name].hist, samp.name)

        for name, hist in histsD.items():
            hist.normalize_lumi(lumi_total)

        for samp in samples_data:
            histsD[samp.name] = samp.drawHistogram(var, str(cut), plot_range=plot_range)
            Styling.data_style(histsD[samp.name].hist)

        hists_thD = dict()
        for (k,v) in histsD.items():
            hists_thD[k] = v.hist

        merge_cmd = copy.deepcopy(merge_cmds)
        merge_cmd["QCD (MC)"] = ["QCDMu"]
        merged = merge_hists(hists_thD, merge_cmd)

        stack = dict()
        stack["mc"] = [merged[name] for name in merged.keys() if name!="single #mu"]
        stack["data"] = [merged["single #mu"]]

        canv = ROOT.TCanvas()
        pl = plot_hists_stacked(canv, stack, **kwargs)
        leg = legend(stack["data"] + stack["mc"][::-1], **kwargs)
        lb = lumi_textbox(lumi_total)
        canv.SaveAs(kwargs.get("filename", "plot") + ".pdf")
        return stack, canv, pl, leg, lb

    cut = Cuts.no_cut
    cutname = "hlt"

    ret1 = compare_plot("cos_theta", [20, -1, 1], "1.0", cut, filename="cos_theta_"+cutname)
    ret1A = compare_plot("mu_pt", [20, 0, 200], "1.0", cut, do_log_y=True, filename="mu_pt_"+cutname, x_label="pt_{#mu} [GeV]",
        min_bin=10, max_bin_mult=100)
    #ret1B = compare_plot("abs(mu_eta)", [20, 0, 3.0], "1.0", cut, do_log_y=True, filename="mu_eta_"+cutname, x_label="#eta_{#mu}",
    #    min_bin=10, max_bin_mult=100)
    ret2 = compare_plot("mu_db", [20, 0, 1.2*0.2], "1.0", cut, do_log_y=True, filename="mu_db_"+cutname, x_label="db_{#mu} [cm]",
        min_bin=10, max_bin_mult=100)
    ret3 = compare_plot("abs(mu_dz)", [20, 0, 1.2*0.5], "1.0", cut, do_log_y=True, filename="mu_dz_"+cutname, x_label="|dz_{#mu}| [cm]",
        min_bin=10, max_bin_mult=100)
    ret4 = compare_plot("mu_iso", [20, 0, 0.15], "1.0", cut, do_log_y=True, filename="mu_iso_"+cutname, x_label="Iso_{#mu}",
        min_bin=10, max_bin_mult=100)

    ret5 = compare_plot("mu_gtrack", [21, 0, 20], "1.0", cut, do_log_y=True, filename="mu_gtrack_"+cutname, x_label="gtrack_{#mu}",
        min_bin=10, max_bin_mult=100)
    ret6 = compare_plot("mu_layers", [21, 0, 20], "1.0", cut, do_log_y=True, filename="mu_layers_"+cutname, x_label="layers_{#mu}",
        min_bin=10, max_bin_mult=100)
    ret7 = compare_plot("mu_itrack", [7, 0, 6], "1.0", cut, do_log_y=True, filename="mu_itrack_"+cutname, x_label="itrack_{#mu}",
        min_bin=10, max_bin_mult=100)
    ret8 = compare_plot("mu_stations", [7, 0, 6], "1.0", cut, do_log_y=True, filename="mu_stations_"+cutname, x_label="stations_{#mu}",
        min_bin=10, max_bin_mult=100)
