from project_histos import Cuts, filter_alnum, Sample
from make_plots import plot_hists, canvas_margin, legend
import argparse
if __name__=="__main__":

    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    
    #fname = "/Users/joosep/Documents/stpol/data/step3_trees_Mar28/T_t.root"
    fnames = [
        "/Users/joosep/Documents/stpol/data/T_t.root",
        "/Users/joosep/Documents/stpol/data/step3_trees_Apr04/iso/mc/T_t.root",
        "/Users/joosep/Documents/stpol/data/step3_trees_Apr05_noPuClean/iso/mc/T_t.root",
    ]
    samples = [Sample.fromFile(f) for f in fnames]
    sample_names = ["Apr16 (fixed norm)", "Apr04", "Apr05 (no PU cl.)"]
    
    samps = zip(samples, sample_names)
    cut = Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig

    hists = []
    for sample, name in samps:
        hist = sample.drawHistogram("cos_theta", cut.cut_str, plot_range=[40, -1, 1])
        
        #normalize to 20/fb
        hist.normalize_lumi(20000)
        
        hist.hist.SetName(name)
        hist.hist.SetTitle("%s: %.3E" % (name, hist.hist.Integral()))
        hist.update()
        
        hists.append(hist)
        print "%s: %.3E" % (name, hist.hist.Integral())

    title = "%s cos-theta with different processings" % sample.name
    title += " normalized to 20/fb"
        
    canv = plot_hists(hists, do_log_y=False, title=title, x_label="cos #theta")
    leg = legend(hists, pos="top-right-small")
    canv.SaveAs("final_plot.pdf")
    #canvas_margin(canv, 0.3)