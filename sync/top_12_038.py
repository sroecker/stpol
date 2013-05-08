import sys
import os
import copy
#sys.path.append(os.environ["STPOL_DIR"])

import plots
import plots.common
from plots.project_histos import Sample, Cuts
from plots.common.utils import merge_cmds, merge_hists

sample_dir = "/scratch/joosep/out_step3_05_07_14_19/iso/mc"

samples = []
samples.append(Sample.fromFile(sample_dir + "/TTJets_MassiveBinDECAY.root"))
#samples.append(project_histos.Sample.fromFile(sample_dir + "TTJets_SemiLept.root"))
samples.append(Sample.fromFile(sample_dir + "/T_t.root"))
samples.append(Sample.fromFile(sample_dir + "/Tbar_t.root"))
samples.append(Sample.fromFile(sample_dir + "/QCDMu.root"))
samples.append(Sample.fromFile(sample_dir + "/WJets_inclusive.root"))

def mc_amount(cut, weight, lumi=12210, ref=None):
    histsD = dict()
    for samp in samples:
        histsD[samp.name] = samp.drawHistogram("n_tags", str(cut), dtype="int", weight=weight, plot_range=[4, 0, 4])

    for name, hist in histsD.items():
        hist.normalize_lumi(lumi)
    for name, hist in histsD.items():
        histsD[name] = hist.hist
    merge_cmd = dict()
    merge_cmd["t-channel"] = ["T_t", "Tbar_t"]
    merge_cmd["QCD (MC)"] = ["QCDMu"]
    merge_cmd["t#bar{t} incl."] = ["TTJets_MassiveBinDECAY"]
    merge_cmd["WJets incl"] = ["WJets_inclusive"]
    merged_hists = merge_hists(histsD, merge_cmd)

    normd = dict()
    for hn, h in merged_hists.items():
        normd[hn] = h.Integral()
    return merged_hists, normd


if __name__=="__main__":
    cut = Cuts.mu * Cuts.n_jets(2) * Cuts.mt_mu * Cuts.top_mass_sig * Cuts.eta_lj
    hists, norms = mc_amount(cut, "1.0")
