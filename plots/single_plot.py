import ROOT
from project_histos import Sample, Cuts, Cut
import argparse
from common.odict import OrderedDict as dict
#from make_plots import plot_hists_stacked, Styling, merge_hists_g, g_merge_cmd, legend
import copy
from common.utils import merge_cmds, merge_hists

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="iso")
    parser.add_argument("-d", "--dir", type=str, default="/Users/joosep/Documents/stpol/data/step3_trees_Apr04")
    lumi_total = 18062
    args = parser.parse_args()

    samples_mc = Sample.fromDirectory(args.dir + "/" + args.type + "/mc")
    samples_data = Sample.fromDirectory(args.dir + "/" + args.type + "/data")

#    def compare_plot(var, plot_range, weight, cut, **kwargs):
#        histsD = dict()
#
#        for samp in samples_mc:
#            histsD[samp.name] = samp.drawHistogram(var, str(cut), weight=weight, plot_range=plot_range)
#
#        for name, hist in histsD.items():
#            hist.normalize_lumi(lumi_total)
#
#        for samp in samples_data:
#            histsD[samp.name] = samp.drawHistogram(var, str(cut), plot_range=plot_range)
#
#
#        merge_cmd = g_merge_cmd
#        merge_cmd["QCD (MC)"] = ["QCDMu"]
#        merged_hists = merge_hists_g(histsD, merge_cmd)
#
#        stack = dict()
#        stack["mc"] = [merged_hists[name] for name in merged_hists.keys() if name!="data"]
#        stack["data"] = [merged_hists["data"]]
#
#
#        canv, stacks = plot_hists_stacked(
#                stack,
#                styles=Styling.style, draw_styles={"data": "E1"},
#                **kwargs
#        )
#        leg = legend(stack["data"] + stack["mc"], styles=["p", "f"])
#
#        return canv, stacks, leg

    def mc_amount(cut, weight, lumi, ref=None):
        histsD = dict()
        for samp in samples_mc:
            histsD[samp.name] = samp.drawHistogram("eta_lj", str(cut), weight=weight, plot_range=[100,-5,5])

        for name, hist in histsD.items():
            hist.normalize_lumi(lumi)
        for name, hist in histsD.items():
            histsD[name] = hist.hist
        merge_cmd = copy.deepcopy(merge_cmds)
        merge_cmd["QCD (MC)"] = ["QCDMu"]
        merge_cmd["t#bar{t} incl."] = ["TTJets_MassiveBinDECAY"]
        merge_cmd.pop("data")
        merged_hists = merge_hists(histsD, merge_cmd)

        interesting = ["t#bar{t}", "t#bar{t} incl.", "W(#rightarrow l #nu) + jets", "QCD (MC)", "t-channel"]

        for i in interesting:
            r = 0.0
            r0 = 0.0
            if ref and i in ref.keys():
                r0 = ref[i]
                r = 100.0*merged_hists[i].Integral() / float(r0)
            print "%s | %d | %d | %.2f %%" % (i, merged_hists[i].Integral(), r0, r)


    weight = "pu_weight*muon_IDWeight*muon_IsoWeight"
    doCutFlow = True
    if doCutFlow:
        print "1 iso mu, 0 veto mu/ele"
        ref = dict()
        ref["t#bar{t}"] = 261429
        ref["t#bar{t} incl."] = ref["t#bar{t}"]
        ref["W(#rightarrow l #nu) + jets"] = 47758738
        ref["QCD (MC)"] = 1873957
        ref["t-channel"] = 54769
        previous = Cuts.hlt_isomu * Cuts.one_muon * Cuts.lepton_veto
        mc_amount(previous, weight, 12210, ref=ref)
        print

        print "2 jets"
        ref = dict()
        ref["t#bar{t}"] = 78201
        ref["t#bar{t} incl."] = ref["t#bar{t}"]
        ref["W(#rightarrow l #nu) + jets"] = 921051
        ref["QCD (MC)"] = 67463
        ref["t-channel"] = 20274
        previous = previous*Cuts.n_jets(2)*Cuts.eta_jet*Cuts.pt_jet
        mc_amount(previous, weight, 12210, ref=ref)
        print

        print "met>45"
        ref = dict()
        ref["t#bar{t}"] = 50158
        ref["t#bar{t} incl."] = ref["t#bar{t}"]
        ref["W(#rightarrow l #nu) + jets"] = 418873
        ref["QCD (MC)"] = 8090
        ref["t-channel"] = 10828
        previous = previous * Cut("met > 45")
        mc_amount(previous, weight, 12210, ref=ref)
        print

        print "1 tight b-tag"
        ref = dict()
        ref["t#bar{t}"] = 18779
        ref["t#bar{t} incl."] = ref["t#bar{t}"]
        ref["W(#rightarrow l #nu) + jets"] = 6304
        ref["QCD (MC)"] = 601
        ref["t-channel"] = 4060
        previous = previous * Cuts.n_tags(1)
        mc_amount(previous, weight, 12210, ref=ref)
        print

        print "jet rms < 0.025"
        ref = dict()
        ref["t#bar{t}"] = 14960
        ref["t#bar{t} incl."] = ref["t#bar{t}"]
        ref["W(#rightarrow l #nu) + jets"] = 5134
        ref["QCD (MC)"] = 447
        ref["t-channel"] = 4412
        previous = previous * Cuts.rms_lj
        mc_amount(previous, weight, 12210, ref=ref)
        print

    #cut = Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)
    #A = compare_plot("abs(eta_lj)", [10, 0, 5], "1.0", cut, "mt>50, 2J1T, no weight")
    #B = compare_plot("abs(eta_lj)", [10, 0, 5], "pu_weight", cut, "mt>50, 2J1T, pu weight")

    #n_bins = 20
    #do_log_y=False
    #weight

    #A = compare_plot("top_mass", [n_bins, 100, 300], weight, Cut("mu_iso<0.12")*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj,
    #    title="M_{t}>50 GeV, 2J1T, |#eta_{lj}| > 2.5, rms_{lj}<0.025", do_log_y=do_log_y, x_label="M_{bl#nu} [GeV]"
    #)
    #A[0].SaveAs("top_mass_2J1T.png")

    #B = compare_plot("top_mass", [n_bins, 100, 300], weight, Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.eta_lj*Cuts.rms_lj,
    #    title="M_{t}>50 GeV, 2J0T, |#eta_{lj}| > 2.5, rms_{lj}<0.025", do_log_y=do_log_y, x_label="M_{bl#nu} [GeV]"
    #)
    #B[0].SaveAs("top_mass_2J0T.png")

    #C = compare_plot("top_mass", [n_bins, 100, 300], weight, Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(0)*Cuts.eta_lj*Cuts.rms_lj,
    #    title="M_{t}>50 GeV, 3J0T, |#eta_{lj}| > 2.5, rms_{lj}<0.025", do_log_y=do_log_y, x_label="M_{bl#nu} [GeV]"
    #)
    #C[0].SaveAs("top_mass_3J0T.png")

    #D = compare_plot("top_mass", [n_bins, 100, 300], weight, Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj,
    #    title="M_{t}>50 GeV, 3J1T, |#eta_{lj}| > 2.5, rms_{lj}<0.025", do_log_y=do_log_y, x_label="M_{bl#nu} [GeV]"
    #)
    #D[0].SaveAs("top_mass_3J1T.png")

#    B = compare_plot("abs(eta_lj)", [n_bins, 0, 5], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")
#    C = compare_plot("pt_lj", [n_bins, 0, 300], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")
#    D = compare_plot("abs(eta_bj)", [n_bins, 0, 5], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")
#    E = compare_plot("pt_bj", [n_bins, 0, 300], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")
#    E = compare_plot("mu_iso", [n_bins, 0, 0.15], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")
#    E = compare_plot("mu_pt", [n_bins, 0, 300], "1.0", Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.rms_lj, "mu")


