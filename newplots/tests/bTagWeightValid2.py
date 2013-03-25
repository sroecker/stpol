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

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")

class TObjectOpenException(Exception): pass

def filter_alnum(s):
    """Filter out everything except ascii letters and digits"""
    return filter(lambda x: x in string.ascii_letters+string.digits + "_", s)

class Histogram(Base):
    __tablename__ = "histograms"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    n_entries = Column(Integer)

    var = Column(String)
    cut = Column(String)
    weight = Column(String)
    sample_name = Column(String)
    sample_entries = Column(String)
    hist_dir = Column(String)
    hist_file = Column(String)

    #def __init__(self, hist, *args, **kwargs):
    #    super(Histogram, self).__init__(*args, **kwargs)
    #    self.hist = None

    def setHist(self, hist, **kwargs):
        self.hist = hist
        self.name = str(self.hist.GetName())
        self.n_entries = int(kwargs["n_entries"])
        self.var = kwargs["var"]
        self.cut = kwargs["cut"]
        self.weight = kwargs["weight"]
        self.sample_name = kwargs["sample_name"]
        self.sample_entries = kwargs["sample_entries"]
        self.update()

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


#    def __getstate__(self):
#        self.hist_name = self.hist.GetName()
#        self.hist_dir = self.hist.GetDirectory().GetName()
#        d = copy.deepcopy(self.__dict__)
#        d.pop("hist")
#        return d
#
#    def __setstate__(self, d):
#        self.__dict__.update(d)
#        self.hist = ROOT.gDirectory.Get(self.hist_dir).Get(self.hist_name)

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
        self.logger.info("Opened sample %s with %d final events, %d processed" % (self.name, self.getEventCount(), self.getTotalEventCount()))

    def getEventCount(self):
        if self.event_count is None:
            self.event_count = self.tree.GetEntries()
        return self.event_count

    def getTotalEventCount(self):
        count_hist = self.tfile.Get("trees").Get("count_hist")
        if not count_hist:
            raise TObjectOpenException("Failed to open count histogram")
        return count_hist.GetBinContent(1)

    def drawHistogram(self, var, cut, name, **kwargs):
        plot_range = kwargs["plot_range"]

        if "weight" in kwargs.keys():
            weight_str = kwargs["weight"]
        else:
            weight_str = "1.0"

        ROOT.TH1.AddDirectory(False)
        hist = ROOT.TH1F("htemp", "htemp", plot_range[0], plot_range[1], plot_range[2])
        hist.Sumw2()
        hist.SetDirectory(ROOT.gROOT)
        #hist.SetBit(ROOT.TH1.kCanRebin)
        ROOT.gROOT.cd()
        n_entries = self.tree.Draw(var + ">>htemp", weight_str + "*" + cut, "goff")
        hist.SetDirectory(0)
        #hist = ROOT.gROOT.Get("htemp")
        if not hist or hist.GetEntries() != n_entries:
            raise TObjectOpenException("Could not get histogram: %s" % hist)
        #pdb.set_trace()
        #hist_new = ROOT.TH1F(hist)
        hist_new = hist.Clone(filter_alnum(name))
        #hist.Delete()
        #del hist
        hist = hist_new
        hist.SetTitle(name)
        hist_ = Histogram()
        hist_.setHist(hist, n_entries=n_entries, var=var, cut=cut, weight=kwargs["weight"] if "weight" in kwargs.keys() else None, sample_name=self.name, sample_entries=self.getTotalEventCount())
        return hist_

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
        dirA = self.tfile.mkdir(filter_alnum(cut))
        if not dirA:
            self.tfile.cd(filter_alnum(cut))
            dirA = self.tfile.Get(filter_alnum(cut))

        histos = list()

        for sample in self.samples:
            hist = sample.drawHistogram(var, cut, sample.name + "_" + var + "_" + cut + "_" + (kwargs["weight"] if "weight" in kwargs.keys() else ""), **kwargs)

            dirA.cd()
            hist.hist.Write()
            hist.update(file=self.tfile, dir=dirA)
            histos += [hist]
            self.tfile.Write()
        return histos

if __name__=="__main__":
    engine = create_engine('sqlite:///histos.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    Base.metadata.create_all(engine)

    samples = list()
    samples = Sample.fromDirectory("/Users/joosep/Documents/stpol/data/")
    #samples = [Sample.fromFile("/Users/joosep/Documents/stpol/TTJets_FullLept_sf.root")]

    histos = dict()
    hdraw = HistoDraw("histos.root", samples)

    histos = []
    b_weight_range = [100, 1.02, 1.3]
    histos += hdraw.drawHistogram("b_weight_nominal", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", cut="n_tags==0.0", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", cut="n_tags==0.0 && true_b_count==0.0", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", cut="n_tags==0.0 && true_b_count==1.0", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", cut="n_tags==0.0 && true_b_count==2.0", plot_range=b_weight_range)
    histos += hdraw.drawHistogram("b_weight_nominal", cut="n_tags==0.0 && true_b_count==3.0", plot_range=b_weight_range)
#    histos += hdraw.drawHistogram("scale_factors", cut="n_tags==0.0 && true_b_count==3.0", plot_range=[40, 0, 2])

    histos += hdraw.drawHistogram("true_b_count", plot_range=[4, 0, 4])
    histos += hdraw.drawHistogram("n_tags", plot_range=[4, 0, 4])
    histos += hdraw.drawHistogram("true_b_tagged_count", plot_range=[4, 0, 4])

    for h in histos:
        session.add(h)
    #session.flush()
    session.commit()

    #info = ROOT.TObjString(pickle.dumps(histos))
    #hdraw.tfile.WriteObject(info, "histo_info")
    hdraw.tfile.Close()
