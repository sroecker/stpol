from project_histos import Cuts, filter_alnum, Sample
from make_plots import plot_hists, canvas_margin, legend
import argparse
from collections import OrderedDict as dict

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', type=str, required=True)
    parser.add_argument('--normalize_lumi', action="store_true", default=True)
    args = parser.parse_args()

    #fname = "/Users/joosep/Documents/stpol/data/step3_trees_Mar28/T_t.root"
    sample = Sample.fromFile(args.infile)

#    ev_ids = dict()
#    for ev in sample.tree:
#        evid = int(ev.event_id)
#        if evid not in ev_ids.keys():
#            ev_ids[evid] = 1
#        else:
#            ev_ids[evid] += 1

    cuts = dict()
    cuts["MT_mu"] = Cuts.mt_mu
    cuts["2J"] = Cuts.n_jets(2)
    cuts["1T"] = Cuts.n_tags(1)
    #cuts["eta_lj"] = Cuts.eta_lj
    cuts["rms_lj"] = Cuts.rms_lj
    cuts["eta_jet"] = Cuts.eta_jet
    cuts["top_mass_sig"] = Cuts.top_mass_sig

    def makeSequences(cutsD):
        cuts = cutsD.values()
        cut_sequences = [cuts[0]]
        for cut in cuts[1:]:
            new_sequence = cut_sequences[-1]*cut
            cut_sequences.append(new_sequence)
        return cut_sequences

    sequences = makeSequences(cuts)

    hists = []
    for (cut, name) in zip(sequences, cuts.keys()):
        hist = sample.drawHistogram("cos_theta", cut.cut_str,
            plot_range=[40, -1, 1],
            weight="muon_IDWeight*muon_IsoWeight*pu_weight*b_weight_nominal"
        )
        lumi = 12210
        if args.normalize_lumi:
            hist.normalize_lumi(lumi)

        hist.hist.SetName(name)
        hist.hist.SetTitle("%s: %.3E" % (name, hist.hist.Integral()))
        hist.update()

        hists.append(hist)
        print "%s: %d" % (name, hist.hist.Integral())

    title = "%s cos-theta cutflow" % sample.name
    if args.normalize_lumi:
        title += " normalized to %.1f/fb" % (lumi/1000.0)

    canv = plot_hists(hists, do_log_y=False, title=title, x_label="cos #theta")
    leg = legend(hists, pos="top-right-small")
    canv.SaveAs("cutflow_%s.pdf" % sample.name)
    #canvas_margin(canv, 0.3)
