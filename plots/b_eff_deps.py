import ROOT
from common.histogram import Histogram

f = ROOT.TFile("data/b_effs/T_t.root")

def tagEff2D(fi, flavour, rebin=50):
    hist_true = fi.Get("b_eff_hists/true_%s" % flavour)
    hist_true_tagged = fi.Get("b_eff_hists/true_%s_tagged" % flavour)

    hist_true.Sumw2()
    hist_true_tagged.Sumw2()
    hist_true.Rebin2D(rebin, rebin)
    hist_true_tagged.Rebin2D(rebin, rebin)
    hist_true.Add(hist_true_tagged)

    ROOT.gROOT.cd()

    div = hist_true_tagged.Clone("div_%s" % flavour)
    div.Divide(hist_true)
    return div

def tagEff1D(fi, flavour, rebin=50, proj="x"):
    sample_name = fi.GetPath().split("/")[-2].split(".")[0]

    hist_true = fi.Get("b_eff_hists/true_%s" % flavour)
    hist_true_tagged = fi.Get("b_eff_hists/true_%s_tagged" % flavour)

    if proj=="x":
        true_proj = hist_true.ProjectionX()
        true_tagged_proj = hist_true_tagged.ProjectionX()
    elif proj=="y":
        true_proj = hist_true.ProjectionY()
        true_tagged_proj = hist_true_tagged.ProjectionY()
    else:
        raise ValueError("proj must be x or y")
    true_proj.Sumw2()
    true_tagged_proj.Sumw2()
    true_proj.Rebin(rebin)
    true_tagged_proj.Rebin(rebin)
    true_proj.Add(true_tagged_proj)

    ROOT.gROOT.cd()

    div = true_tagged_proj.Clone("div_%s" % flavour)
    div.Divide(true_proj)
    divh = Histogram.make(div, sample_name=sample_name)
    return divh

def get_eff_norm(sample, flavour, proj, rebin=50):
    ROOT.gROOT.cd()
    hi_true = sample.tfile.Get("b_eff_hists/true_%s" % flavour).Clone()
    hi_tagged = sample.tfile.Get("b_eff_hists/true_%s_tagged" % flavour).Clone()
    hi_true.Sumw2()
    hi_tagged.Sumw2()
    hi_true.Rebin2D(rebin, rebin)
    hi_tagged.Rebin2D(rebin, rebin)

    if proj=="x":
        hi_true = hi_true.ProjectionX()
        hi_tagged = hi_tagged.ProjectionX()
    elif proj=="y":
        hi_true = hi_true.ProjectionY()
        hi_tagged = hi_tagged.ProjectionY()
    hi_true = Histogram.make(hi_true, sample_name=sample.name, sample_entries_total=sample.getTotalEventCount())
    hi_tagged = Histogram.make(hi_tagged, sample_name=sample.name, sample_entries_total=sample.getTotalEventCount())

    hi_true.normalize_lumi(1.0)
    hi_tagged.normalize_lumi(1.0)

    return (hi_true.hist, hi_tagged.hist)

def get_eff_merged(samples, flavour, proj="x"):
    hists = [get_eff_norm(sample, flavour, proj) for sample in samples]

    n_true = hists[0][0]
    n_tagged = hists[0][1]
    n_true.Add(n_tagged)
    for h_true, h_tagged in hists[1:]:
        print "int_true=%.2f, int_tagged=%.2f" % (n_true.Integral(), n_tagged.Integral())
        n_true.Add(h_true)
        n_true.Add(h_tagged)
        n_tagged.Add(h_tagged)
    print "int_true=%.2f, int_tagged=%.2f" % (n_true.Integral(), n_tagged.Integral())
    div = n_tagged.Clone("eff_%s" % flavour)
    div.Divide(n_true)
    print "div=%.2f" % div.Integral()
    return div
