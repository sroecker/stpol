from project_histos import Cuts, filter_alnum, Sample
from make_plots import plot_hists, canvas_margin, legend
import argparse
if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infile', type=str, required=True)
    parser.add_argument('--normalize_lumi', action="store_true")
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
    sequential_cuts = [Cuts.hlt_isomu, Cuts.mt_mu, Cuts.n_jets(2), Cuts.n_tags(1), Cuts.eta_lj, Cuts.top_mass_sig]
    cut_names = ["hlt_isomu", "MT_mu", "2J", "1T", "etalj", "Mtop"]

    def makeSequences(cuts):
        cut_sequences = [cuts[0]]
        for cut in cuts[1:]:
            new_sequence = cut_sequences[-1]*cut
            cut_sequences.append(new_sequence)
        return cut_sequences

    sequences = makeSequences(sequential_cuts)

    hists = []
    for (cut, name) in zip(sequences, cut_names):
        hist = sample.drawHistogram("cos_theta", cut.cut_str, plot_range=[40, -1, 1])

        #normalize to 20/fb
        if args.normalize_lumi:
            hist.normalize_lumi(12210)

        hist.hist.SetName(name)
        hist.hist.SetTitle("%s: %.3E" % (name, hist.hist.Integral()))
        hist.update()

        hists.append(hist)
        print "%s: %d" % (name, hist.hist.Integral())

    title = "%s cos-theta cutflow" % sample.name
    if args.normalize_lumi:
        title += " normalized to 20/fb"

    canv = plot_hists(hists, do_log_y=False, title=title, x_label="cos #theta")
    leg = legend(hists, pos="top-right-small")
    canv.SaveAs("cutflow_%s.pdf" % sample.name)
    #canvas_margin(canv, 0.3)
