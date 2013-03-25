import ROOT
import logging
import pickle
import copy
import pdb
import string
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
from sqlalchemy import Column, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import numpy

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")

class TObjectOpenException(Exception): pass
class HistogramException(Exception): pass

def filter_alnum(s):
    """Filter out everything except ascii letters and digits"""
    return filter(lambda x: x in string.ascii_letters+string.digits + "_", s)

class Cuts:
    top_mass = "top_mass > 130 && top_mass < 220"
    eta_lj = "eta_lj > 2.5"
    mt_mu = "mt_mu > 50"

    @staticmethod
    def n_jets(n):
        return "n_jets == %.1f" % float(n)
    @staticmethod
    def n_tags(n):
        return "n_tags == %.1f" % float(n)



class Histogram(Base):
    __tablename__ = "histograms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    histogram_entries = Column(Integer)

    var = Column(String)
    cut = Column(String)
    weight = Column(String)
    sample_name = Column(String)
    sample_entries_cut = Column(Integer)
    sample_entries_total = Column(Integer)
    hist_dir = Column(String)
    hist_file = Column(String)

    #def __init__(self, hist, *args, **kwargs):
    #    super(Histogram, self).__init__(*args, **kwargs)
    #    self.hist = None

    def setHist(self, hist, **kwargs):
        self.hist = hist
        self.name = str(self.hist.GetName())
        self.histogram_entries = int(kwargs["histogram_entries"])
        self.var = kwargs["var"]
        self.cut = kwargs["cut"]
        self.weight = kwargs["weight"]
        self.sample_name = kwargs["sample_name"]
        self.sample_entries_cut = kwargs["sample_entries_cut"]
        self.sample_entries_total = kwargs["sample_entries_total"]
        self.integral = None
        self.err = None
        self.is_normalized = False
        self.update()

    def calc_int_err(self):
        err = ROOT.Double()
        integral = self.hist.IntegralAndError(1, self.hist.GetNbinsX(), err)
        self.err = err
        self.integral = integral
        return (self.integral, self.err)

    def normalize(self, target=1.0):
        if self.hist.Integral()>0:
            self.hist.Scale(target/self.hist.Integral())
            self.is_normalized = True
        else:
            logging.warning("Histogram %s integral=0, not scaling." % str(self))

    def normalize_lumi(self, lumi=1.0):
        expected_events = sample_xs_map[self.sample_name] * lumi
        total_events = self.getTotalEvents()
        scale_factor = float(expected_events)/float(total_events)
        hist.Scale(scale_factor)


    def update(self, file=None, dir=None):
        self.name = str(self.hist.GetName())
        if file and dir:
            self.hist_dir = dir.GetName()
            self.hist_file = file.GetName()
        else:
            try:
                self.hist_dir = self.hist.GetDirectory().GetName()
            except ReferenceError as e:
                self.hist_dir = None
            try:
                self.hist_file = self.hist.GetDirectory().GetFile().GetName()
            except ReferenceError as e:
                self.hist_file = None

    def loadFile(self):
        self.fi = ROOT.TFile(self.hist_file)
        self.hist = self.fi.Get(self.hist_dir).Get(self.name)
        self.update()

    def __repr__(self):
        return "<Histogram(%s, %s, %s)>" % (self.var, self.cut, self.weight)

    def unique_name(self):
        cut_str = self.cut if self.cut is not None else "NOCUT"
        weight_str = self.weight if self.weight is not None else "NOWEIGHT"
        return filter_alnum(self.var + "_" + cut_str + "_" + weight_str)

class Sample:
    logger = logging.getLogger("Sample")
    def __init__(self, name, file_name):
        self.name = name
        self.file_name = file_name

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

    def drawHistogram(self, var, cut, name, **kwargs):

        if(var not in self.getBranches()):
            raise KeyError("Plot variable %s not defined in branches" % var)

        plot_range = kwargs["plot_range"]

        if "weight" in kwargs.keys():
            weight_str = kwargs["weight"]
        else:
            weight_str = "1.0"

        ROOT.TH1.AddDirectory(False)
        hist = ROOT.TH1F("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])
        hist.Sumw2()

        hist.SetDirectory(ROOT.gROOT)
        ROOT.gROOT.cd()
        n_entries = self.tree.Draw(var + ">>htemp", weight_str + "*" + cut, "goff")

        if n_entries<0:
            raise HistogramException("Could not draw histogram")

        if hist.Integral() != hist.Integral():
            raise HistogramException("Histogram had 'nan' Integral(), probably weight was 'nan'")
        hist.SetDirectory(0)
        if not hist or hist.GetEntries() != n_entries:
            raise TObjectOpenException("Could not get histogram: %s" % hist)
        hist_new = hist.Clone(filter_alnum(name))

        hist.Delete()
        hist = hist_new
        hist.SetTitle(name)
        hist_ = Histogram()
        hist_.setHist(hist, histogram_entries=n_entries, var=var,
            cut=cut, weight=kwargs["weight"] if "weight" in kwargs.keys() else None,
            sample_name=self.name,
            sample_entries_total=self.getTotalEventCount(),
            sample_entries_cut=self.getEventCount(),
            
        )
        hist_.hist.SetName(self.name + "_" + hist_.unique_name())
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


class HistoDraw:
    def __init__(self, file_name, samples):
        self.tfile = ROOT.TFile(file_name, "RECREATE")
        self.samples = samples

    def drawHistogram(self, var, cut="1", **kwargs):
        histos = dict()
        self.tfile.cd()
        if "range" in kwargs.keys():
            plot_range = kwargs["range"]
        else:
            plot_range = None

        cut_dir_name = filter_alnum(cut)
        if not self.tfile.GetListOfKeys().FindObject(cut_dir_name):
            dirA = self.tfile.mkdir(cut_dir_name)
        else:
            self.tfile.cd(filter_alnum(cut))
            dirA = self.tfile.Get(filter_alnum(cut))

        histos = list()

        for sample in self.samples:
            hist = sample.drawHistogram(
                var, cut,
                sample.name + "_" + var + "_" + cut + "_" + (kwargs["weight"] if "weight" in kwargs.keys() else ""),
                **kwargs
            )

            dirA.cd()
            hist.hist.Write()
            hist.update(file=self.tfile, dir=dirA)
            histos += [hist]
            self.tfile.Write()
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

def getBTaggingEff(sample, flavour, cut):
    if flavour not in ["b", "c", "l"]:
        raise ValueError("Flavour must be b, c or l")

    N_tagged = numpy.sum(sample.getColumn("true_%s_tagged_count" % flavour, cut))
    N = numpy.sum(sample.getColumn("true_%s_count" % flavour, cut))
    return N_tagged/N

if __name__=="__main__":

    metadata = MetaData("histos.db", create_new=True)
    samples = list()
    samples = Sample.fromDirectory("/Users/joosep/Documents/stpol/data/")
    samplesDict = dict()
    for sample in samples:
        samplesDict[sample.name] = sample
    #samples = [Sample.fromFile("/Users/joosep/Documents/stpol/TTJets_FullLept_sf.root")]

    histos = dict()
    hdraw = HistoDraw("histos.root", samples)

    histos = []
    b_weight_range = [100, 0.7, 1.5]

    class Cleanup:
        def __init__(self, metadata, hdraw):
            self.metadata = metadata
            self.hdraw = hdraw
        def __enter__(self):
            pass
        def __exit__(self, type, value, traceback):
            self.metadata.session.close_all()
            self.hdraw.tfile.Write()
            self.hdraw.tfile.Close()
            #del self.hdraw
            print value

    with Cleanup(metadata, hdraw):
        try:
            histos += hdraw.drawHistogram("b_weight_nominal", plot_range=b_weight_range)
            #histos += hdraw.drawHistogram("eta_lj", plot_range=[40, -5, 5], weight="b_weight_nominal")
            histos += hdraw.drawHistogram("eta_lj", plot_range=[40, -5, 5])
            histos += hdraw.drawHistogram("eta_lj", cut=Cuts.top_mass, plot_range=[40, -5, 5])
            histos += hdraw.drawHistogram("eta_lj", cut=Cuts.n_jets(2), plot_range=[40, -5, 5])
            for h in histos:
                metadata.save(h)
            logging.info("Done saving to histos.db")
        except Exception as e:
            logging.error("Caught exception %s while drawing histograms, cleaning up and quitting" % str(e))
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


