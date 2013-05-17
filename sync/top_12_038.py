import sys
import os
import copy
sys.path.append(os.environ["STPOL_DIR"])

import plots
import plots.common
from plots.common.odict import OrderedDict as dict
from plots.common.sample import Sample
from plots.common.cuts import Cuts
from plots.common.utils import merge_cmds, merge_hists, get_hist_int_err

lumi_total=12210
sample_dir = "data/out_step3_05_11_23_10/iso/mc/"

samples = []
samples.append(Sample.fromFile(sample_dir + "/TTJets_MassiveBinDECAY.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_FullLept.root"))
samples.append(Sample.fromFile(sample_dir + "/TTJets_SemiLept.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t_ToLeptons.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t_ToLeptons.root"))
samples.append(Sample.fromFile(sample_dir + "/QCDMu.root"))
samples.append(Sample.fromFile(sample_dir + "/WJets_inclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W1Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W2Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W3Jets_exclusive.root"))
samples.append(Sample.fromFile(sample_dir + "/W4Jets_exclusive.root"))

def mc_amount(cut, weight, lumi=12210, ref=None):
    histsD = dict()
    for samp in samples:
        histsD[samp.name] = samp.drawHistogram("mu_pt", str(cut), dtype="float", weight=weight, plot_range=[100, 0, 100000000])

    for name, hist in histsD.items():
        hist.normalize_lumi(lumi)
    for name, hist in histsD.items():
        histsD[name] = hist.hist
    merge_cmd = dict()
    merge_cmd["t-channel incl"] = ["T_t", "Tbar_t"]
    merge_cmd["t-channel excl"] = ["T_t_ToLeptons", "Tbar_t_ToLeptons"]
    merge_cmd["t#bar{t} excl."] = ["TTJets_FullLept", "TTJets_SemiLept"]
    merge_cmd["QCD (MC)"] = ["QCDMu"]
    merge_cmd["t#bar{t} incl."] = ["TTJets_MassiveBinDECAY"]
    merge_cmd["WJets incl"] = ["WJets_inclusive"]
    merge_cmd["WJets excl"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
    merged_hists = merge_hists(histsD, merge_cmd)

    normd = dict()
    for hn, h in merged_hists.items():
        normd[hn] = get_hist_int_err(h)
    return merged_hists, normd


if __name__=="__main__":
    #cut = Cuts.mu * Cuts.n_jets(2) * Cuts.mt_mu * Cuts.top_mass_sig * Cuts.eta_lj * Cuts.n_tags(1)
    cut = Cuts.mu * Cuts.final
    hists, norms = mc_amount(cut, "pu_weight*muon_IDWeight*muon_IsoWeight")
    for (samp, (count, err)) in norms.items():
        print "%s: %.0f +- %.0f" % (samp, count, err)
