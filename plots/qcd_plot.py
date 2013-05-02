import ROOT
from project_histos import Sample, Cuts, Cut
import argparse
from collections import OrderedDict as dict
from make_plots import plot_hists_stacked, Styling, merge_hists_g, g_merge_cmd, legend, plot_hists
import copy

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dir", type=str, default="/Users/joosep/Documents/stpol/data/step3_trees_Apr04")
    args = parser.parse_args()

    samples_mc_iso = Sample.fromDirectory(args.dir + "/iso/mc")
    samples_data_iso = Sample.fromDirectory(args.dir + "/iso/data")
    samples_mc_aiso = Sample.fromDirectory(args.dir + "/anti-iso/mc")
    samples_data_aiso = Sample.fromDirectory(args.dir + "/anti-iso/data")
    
    samplesD_iso = dict()
    for sample in samples_mc_iso + samples_data_iso:
        samplesD_iso[sample.name] = sample
    samplesD_aiso = dict()
    for sample in samples_mc_aiso + samples_data_aiso:
        samplesD_aiso[sample.name] = sample

    def qcd_comp_plot(var, cut, plot_range, **kwargs):
        lumi = 6471
        hist_qcd_iso = samplesD_iso["QCDMu"].drawHistogram(var, str(cut), plot_range=plot_range)
        hist_qcd_iso.pretty_name = "simulation: %d ev." % hist_qcd_iso.hist.Integral()
        print "MC qcd events: %d" % hist_qcd_iso.hist.Integral()
        hist_qcd_iso.normalize_lumi(lumi)
        hist_data_aiso = samplesD_aiso["SingleMuD"].drawHistogram(var, str(cut), plot_range=plot_range)
        hist_data_aiso.pretty_name = "data driven"
        hist_data_aiso.normalize(hist_qcd_iso.hist.Integral())
        print hist_qcd_iso.hist.Integral()
        print hist_data_aiso.hist.Integral()
        canv = plot_hists([hist_qcd_iso, hist_data_aiso], **kwargs)
        B = legend([hist_qcd_iso, hist_data_aiso])
        canv.SaveAs(kwargs.get("filename", "qcd_comp.pdf"))
        return canv, B

    var = "abs(eta_lj)"
    plot_range = [10, 2.5, 4.5]
    plot_rangeB = [10, 0, 4.5]
    D = qcd_comp_plot(
        var,
        Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
        plot_range,
        title="QCD dd verification: |#eta_{lj}| in 2J1T, M_{t}(W) > 50 GeV, |#eta_{lj}|>2.5, M_{bl#nu} #in [130, 220] GeV", x_label="|#eta_{lj}|",
        filename="qcd_comp_2J1T_etalj_mtop_mtmu.pdf"
    )
    A = qcd_comp_plot(
        var,
        Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
        plot_range,
        title="QCD dd verification: |#eta_{lj}| in 2J1T, |#eta_{lj}|>2.5, M_{bl#nu} #in [130,220]", x_label="|#eta_{lj}|",
        filename="qcd_comp_2J1T_etalj_mtop.pdf"
    )
    B = qcd_comp_plot(
        var,
        Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj,
        plot_range,
        title="QCD dd verification: |#eta_{lj}| in 2J1T, |#eta_{lj}|>2.5", x_label="|#eta_{lj}|",
        filename="qcd_comp_2J1T_etalj.pdf"
    )

    C = qcd_comp_plot(
        var,
        Cuts.n_jets(2)*Cuts.n_tags(1),
        plot_rangeB,
        title="QCD dd verification: |#eta_{lj}| in 2J1T", x_label="|#eta_{lj}|",
        filename="qcd_comp_2J1T.pdf"
    )