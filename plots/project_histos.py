import ROOT
import logging
import pickle
import copy
import pdb
import string
import sys
import argparse

try:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()
    from sqlalchemy import Column, Integer, String
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except:
    print "project_histos.py: SQLAlchemy needed, please install by running util/install_sqlalchemy.sh"

import os
import numpy
import copy
from common.cross_sections import xs as sample_xs_map
import fnmatch
import itertools

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")

#class TObjectOpenException(Exception): pass
#class HistogramException(Exception): pass
#
#
#class Cut:
#    def __init__(self, cut_str):
#        self.cut_str = cut_str
#    def __mul__(self, other):
#        cut_str = '('+self.cut_str+') && ('+other.cut_str+')'
#        return Cut(cut_str)
#    def __repr__(self):
#        return "<Cut(%s)>" % self.cut_str
#
#    def __str__(self):
#        return self.cut_str
#
#class Cuts:
#    hlt_isomu = Cut("HLT_IsoMu24_eta2p1_v11 == 1 || HLT_IsoMu24_eta2p1_v12 == 1 || HLT_IsoMu24_eta2p1_v13 == 1 || HLT_IsoMu24_eta2p1_v14 == 1 || HLT_IsoMu24_eta2p1_v15 == 1 || HLT_IsoMu24_eta2p1_v16 == 1  || HLT_IsoMu24_eta2p1_v17 == 1")
#    eta_lj = Cut("abs(eta_lj) > 2.5")
#    mt_mu = Cut("mt_mu > 50")
#    rms_lj = Cut("rms_lj < 0.025")
#    eta_jet = Cut("abs(eta_lj) < 4.5")*Cut("abs(eta_bj) < 4.5")
#    pt_jet = Cut("pt_lj > 40")*Cut("pt_bj > 40")
#    top_mass_sig = Cut("top_mass > 130 && top_mass < 220")
#    one_muon = Cut("n_muons==1 && n_eles==0")
#    lepton_veto = Cut("n_veto_mu==0 && n_veto_ele==0")
#    no_cut = Cut("1")
#
#    @staticmethod
#    def n_jets(n):
#        return Cut("n_jets == %d" % int(n))
#    @staticmethod
#    def n_tags(n):
#        return Cut("n_tags == %d" % int(n))
#
#Cuts.final = Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig
#Cuts.mu = Cuts.hlt_isomu*Cuts.one_muon*Cuts.lepton_veto


class Sample:
    def __init__(self, name, file_name):
        self.name = name
        self.file_name = file_name
        self.logger = logging.getLogger(str(self))

        try:
            self.tfile = ROOT.TFile(file_name)
            if not self.tfile:
                raise FileOpenException("Could not open TFile %s: %s" % (self.file_name, self.tfile))
        except Exception as e:
            raise e

        self.tree = self.tfile.Get("trees").Get("Events")
        if not self.tree:
            raise TObjectOpenException("Could not open tree Events from file %s: %s" % (self.tfile.GetName(), self.tree))
        self.tree.SetCacheSize(100*1024*1024)
        #self.tree.AddBranchToCache("*", 1)

        self.event_count = None
        self.event_count = self.getEventCount()
        if self.event_count<=0:
            self.logger.warning("Sample was empty: %s" % self.name)
            #raise Exception("Sample event count was <= 0: %s" % self.name)

        self.isMC = not self.file_name.startswith("Single")

        self.logger.info("Opened sample %s with %d final events, %d processed" % (self.name, self.getEventCount(), self.getTotalEventCount()))

    def getEventCount(self):
        if self.event_count is None:
            self.event_count = self.tree.GetEntries()
        return self.event_count

    def getBranches(self):
        return [x.GetName() for x in self.tree.GetListOfBranches()]

    def getTotalEventCount(self):
        count_hist = self.tfile.Get("trees").Get("count_hist")
        if not count_hist:
            raise TObjectOpenException("Failed to open count histogram")
        return count_hist.GetBinContent(1)

    def drawHistogram(self, var, cut, dtype="float", **kwargs):
        name = self.name + "_" + Histogram.unique_name(var, cut, kwargs.get("weight"))

        #if(var not in self.getBranches()):
        #    raise KeyError("Plot variable %s not defined in branches" % var)

        plot_range = kwargs.get("plot_range", [100, 0, 100])

        weight_str = kwargs.get("weight", None)

        ROOT.gROOT.cd()
        if dtype=="float":
            hist = ROOT.TH1F("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])
        elif dtype=="int":
            hist = ROOT.TH1I("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])

        hist.Sumw2()

        draw_cmd = var + ">>htemp"

        if weight_str:
            cutweight_cmd = weight_str + " * " + "(" + cut + ")"
        else:
            cutweight_cmd = "(" + cut + ")"

        self.logger.debug("Calling TTree.Draw('%s', '%s')" % (draw_cmd, cutweight_cmd))

        n_entries = self.tree.Draw(draw_cmd, cutweight_cmd, "goff")
        self.logger.debug("Histogram drawn with %d entries, integral=%.2f" % (n_entries, hist.Integral()))

        if n_entries<0:
            raise HistogramException("Could not draw histogram")

        if hist.Integral() != hist.Integral():
            raise HistogramException("Histogram had 'nan' Integral(), probably weight was 'nan'")
        if not hist:
            raise TObjectOpenException("Could not get histogram: %s" % hist)
        if hist.GetEntries() != n_entries:
            raise HistogramException("Histogram drawn with %d entries, but actually has %d" % (n_entries, hist.GetEntries()))
        hist_new = hist.Clone(filter_alnum(name))

        hist = hist_new
        hist.SetTitle(name)
        hist_ = Histogram()
        hist_.setHist(hist, histogram_entries=n_entries, var=var,
            cut=cut, weight=kwargs["weight"] if "weight" in kwargs.keys() else None,
            sample_name=self.name,
            sample_entries_total=self.getTotalEventCount(),
            sample_entries_cut=self.getEventCount(),

        )
        return hist_

    def getColumn(self, col, cut):
        N = self.tree.Draw(col, cut, "goff")
        N = int(N)
        if N < 0:
            raise Exception("Could not get column %s: N=%d" % (col, N))
        buf = self.tree.GetV1()
        arr = ROOT.TArrayD(N, buf)
        self.logger.debug("Column retrieved, copying to numpy array")
        out = numpy.copy(numpy.frombuffer(arr.GetArray(), count=arr.GetSize()))
        return out

    def getEntries(self, cut):
        return int(self.tree.GetEntries(cut))

    @staticmethod
    def fromFile(file_name):
        sample_name = (file_name.split(".root")[0]).split("/")[-1]
        sample = Sample(sample_name, file_name)
        return sample

    @staticmethod
    def fromDirectory(directory):
        import glob
        file_names = glob.glob(directory + "/*.root")
        samples = [Sample.fromFile(file_name) for file_name in file_names]
        return samples

    def __repr__(self):
        return "<Sample(%s, %s)>" % (self.name, self.file_name)

    def __str__(self):
        return self.__repr__()


class HistoDraw:
    def __init__(self, file_name, samples):
        self.tfile = ROOT.TFile(file_name, "RECREATE")
        self.samples = samples

    def drawHistogram(self, var, cut=Cut("1"), **kwargs):
        histos = dict()
        self.tfile.cd()
        plot_range = kwargs.get("plot_range")
        skip_weight = kwargs.get("skip_weight", ["Single*"])

        cut_dir_name = filter_alnum(cut.cut_str)
        if not self.tfile.GetListOfKeys().FindObject(cut_dir_name):
            dirA = self.tfile.mkdir(cut_dir_name)
        else:
            self.tfile.cd(cut_dir_name)
            dirA = self.tfile.Get(cut_dir_name)

        histos = list()

        for sample in self.samples:
            try:
                #histo_name = sample.name + "_" + var + "_" + cut_dir_name + "_" + (kwargs["weight"] if "weight" in kwargs.keys() else "")
                sample_args = copy.deepcopy(kwargs)
                if(
                    ("weight" in sample_args.keys()) and
                    (
                        (not sample.isMC) or
                        (sum([fnmatch.fnmatch(sample.name, match) for match in skip_weight]) > 0)
                    )
                ):
                    logging.debug("Not using weights on sample %s" % str(sample))
                    sample_args.pop("weight")

                hist = sample.drawHistogram(
                    var, cut.cut_str,
                    **sample_args
                )

                dirA.cd()
                hist.hist.Write()
                hist.update(file=self.tfile, dir=dirA)
                histos += [hist]
                self.tfile.Write()
            except HistogramException as e:
                logging.error("Caught exception (%s) while drawing histogram for sample %s" % (str(e), str(sample)))
        return histos

class MetaData:
    logger = logging.getLogger("MetaData")
    def __init__(self, fname, create_new=False):
        if create_new:
            try:
                os.remove(fname)
                self.logger.info("Deleted previous metadata file %s" % fname)
            except OSError as e:
                pass

        self.engine = create_engine('sqlite:///%s' % fname)
        Session = sessionmaker(bind = self.engine)
        self.session = Session()
        Base.metadata.create_all(self.engine)
        self.logger.info("Opened connection to metadata database: %s" % str(self.engine))

    def save(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.flush()

    def get_histogram(self, sample_name, var, cut_str=None, weight=None, limit=1):
        hist = None
        for hist_ in self.session.query(Histogram).\
            filter(Histogram.sample_name==sample_name).\
            filter(Histogram.var==var).\
            filter(Histogram.weight==weight).\
            filter(Histogram.cut==cut_str).\
            limit(1):

            hist_.loadFile()
            hist = hist_
        if not hist:
            raise KeyError("No match found for sample_name(%s), var(%s), cut_str(%s), weight(%s)" % (sample_name, var, cut_str, weight))

        return hist

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--type", type=str, default="iso")
    parser.add_argument("-d", "--dir", type=str, default="/Users/joosep/Documents/stpol/data/step3_trees_Apr04")
    args = parser.parse_args()

    samples = list()
    samples = Sample.fromDirectory(args.dir + "/" + args.type + "/data")
    samples += Sample.fromDirectory(args.dir + "/" + args.type + "/mc")
    samplesDict = dict()
    for sample in samples:
        samplesDict[sample.name] = sample

    histos = dict()
    metadata = MetaData("histos_%s.db" % args.type, create_new=True)
    hdraw = HistoDraw("histos_%s.root" % args.type, samples)

    histos = []
    b_weight_range = [100, 0.7, 1.5]

    class Cleanup:
        def __init__(self, metadata, hdraw, histos):
            self.metadata = metadata
            self.hdraw = hdraw
            self.histos = histos
        def __enter__(self):
            pass
        def __exit__(self, type, value, traceback):
            self.metadata.session.close_all()
            self.hdraw.tfile.Write()
            self.hdraw.tfile.Close()
            #del self.hdraw
            print "Done cleanup"

    with Cleanup(metadata, hdraw, histos):
        n_bins = 20
        try:
            histos += hdraw.drawHistogram("mt_mu", cut=Cuts.mu, plot_range=[n_bins, 0, 200])
            histos += hdraw.drawHistogram("mt_mu", cut=Cuts.mu, plot_range=[n_bins, 0, 200], weight="pu_weight")

            histos += hdraw.drawHistogram("n_jets", cut=Cuts.mu*Cuts.mt_mu, plot_range=[5, 1, 5])
            histos += hdraw.drawHistogram("n_tags", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2), plot_range=[3, 0, 2])
            histos += hdraw.drawHistogram("n_tags", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(3), plot_range=[3, 0, 2])

            histos += hdraw.drawHistogram("n_jets", cut=Cuts.mu*Cuts.mt_mu, plot_range=[9, 1, 10], weight="pu_weight")
            histos += hdraw.drawHistogram("n_tags", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2), plot_range=[5, 0, 5], weight="pu_weight")
            histos += hdraw.drawHistogram("n_tags", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(3), plot_range=[5, 0, 5], weight="pu_weight")


            histos += hdraw.drawHistogram("top_mass",
                cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj, plot_range=[n_bins, 100, 350],
            )
            histos += hdraw.drawHistogram("top_mass",
                cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj, plot_range=[n_bins, 100, 350],
                weight="pu_weight"
            )
            histos += hdraw.drawHistogram("top_mass",
                cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj, plot_range=[n_bins, 100, 350],
                weight="pu_weight*b_weight_nominal"
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig, plot_range=[n_bins, -1, 1])

            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight", skip_weights=["SingleMu*"]
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight*b_weight_nominal", skip_weights=["SingleMu*"]
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight", skip_weights=["SingleMu*"]
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight", skip_weights=["SingleMu*"]
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight*b_weight_nominal", skip_weights=["SingleMu*"]
            )
            histos += hdraw.drawHistogram("cos_theta", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, -1, 1], weight="pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight", skip_weights=["SingleMu*"]
            )


            histos += hdraw.drawHistogram("n_vertices", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[50, 0, 50], weight="pu_weight", skip_weights=["SingleMu*"]
            )

            histos += hdraw.drawHistogram("n_vertices", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[50, 0, 50], skip_weights=["SingleMu*"]
            )

            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1)*Cuts.eta_lj*Cuts.top_mass_sig,
                plot_range=[n_bins, 0, 0.1], skip_weights=["SingleMu*"]
            )

            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(0), plot_range=[n_bins, 0, 0.1], weight="pu_weight")
            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(2)*Cuts.n_tags(1), plot_range=[n_bins, 0, 0.1], weight="pu_weight")
            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(0), plot_range=[n_bins, 0, 0.1], weight="pu_weight")
            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(1), plot_range=[n_bins, 0, 0.1], weight="pu_weight")
            histos += hdraw.drawHistogram("rms_lj", cut=Cuts.mu*Cuts.mt_mu*Cuts.n_jets(3)*Cuts.n_tags(2), plot_range=[n_bins, 0, 0.1], weight="pu_weight")

            n_jets = [2,3]
            n_tags = [0,1,2]
            weights = [None, "pu_weight", "pu_weight*b_weight_nominal", "pu_weight*b_weight_nominal*muon_IDWeight*muon_IsoWeight"]
            for nj, nt, weight in itertools.product(n_jets, n_tags, weights):
                histos += hdraw.drawHistogram("eta_lj", cut=Cuts.mu*Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(nj)*Cuts.n_tags(nt), plot_range=[n_bins, -5, 5],
                    weight=weight,
                    skip_weight=["QCD*", "SingleMu*"]
                )
                histos += hdraw.drawHistogram("abs(eta_lj)", cut=Cuts.mu*Cuts.rms_lj*Cuts.mt_mu*Cuts.n_jets(nj)*Cuts.n_tags(nt), plot_range=[n_bins, 0, 5],
                    weight=weight,
                    skip_weight=["QCD*", "SingleMu*"]
                )
            for h in histos:
                metadata.save(h)
            logging.info("Done saving %d histograms." % len(histos))
        except HistogramException as e:
            pass
            #raise e

    do_b_effs = False
    if do_b_effs:
        logging.info("Doing b-tagging efficiency calculations")
        cuts = []
        cuts.append("n_jets==2 && top_mass>130 && top_mass<220 && mt_mu>50")
    #    cuts.append("n_jets==3 && top_mass>130 && top_mass<220 && mt_mu>50")
    #    cuts.append("n_jets==2 && !(top_mass>130 && top_mass<220) && mt_mu>50")
    #    cuts.append("n_jets==3 && !(top_mass>130 && top_mass<220) && mt_mu>50")
        for cut in cuts:
            print cut
            #for sample in ["TTJets_FullLept", "TTJets_SemiLept", "TTJets_MassiveBinDECAY", "T_t", "WJets_inclusive"]:
            for sample in ["TTJets_MassiveBinDECAY", "T_t", "WJets_inclusive"]:
                for flavour in ["b", "c", "l"]:
                    entries = samplesDict[sample].getEntries(cut)
                    total = samplesDict[sample].getTotalEventCount()
                    eff = getBTaggingEff(samplesDict[sample], flavour, cut)
                    print "%s | %s | %.3E/%.3E | %.3E" % (sample, flavour, entries, total, eff)
