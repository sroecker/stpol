import ROOT
import string
import types
import params
import logging
import glob
import numpy
import pdb
import time

from plotfw.params import Cut # FIXME: temporary hack for backwards comp.
from plotfw.params import parent_branch
import plotfw.cross_sections
import copy
from zlib import adler32

class TreeStats:
	def __init__(self, N_entries, N_drawn, time):
		self.N_entries = N_entries
		self.N_drawn = N_drawn
		self.time = time

	def __add__(self, other):
		self.N_entries += other.N_entries
		self.N_drawn += other.N_drawn
		self.time += other.time

	def speedA(self):
		return self.N_entries/self.time

	def speedB(self):
		return self.N_drawn/self.time

	def __str__(self):
		return "{0}/{1} in {2} sec, all evts: {3}/sec, drawn evts: {4}".format(self.N_drawn, self.N_entries, self.time, self.speedA(), self.speedB())
class EmptyTreeException(Exception):
	pass

def th_sep(i, sep=','):
	"""Return a string representation of i with thousand separators"""
	i = abs(int(i))
	if i == 0:
		return '0'
	o = []
	while i > 0:
		o.append(i%1000)
		i /= 1000
	o.reverse()
	return str(sep).join([str(o[0])] + map(lambda x: '%03d'%x, o[1:]))

def filter_alnum(s):
	"""Filter out everything except ascii letters and digits"""
	return filter(lambda x: x in string.ascii_letters+string.digits, s)

class SampleListGenerator:
	"""Helper class that makes it easier to generate sample lists for MC.

	It assumes that all the samples are in the directory.
	It uses the color and cross sections defined in params.py for the
	corresponding sample and group parameters.

	"""
	def __init__(self, directory):
		self._directory = directory
		self._samplelist = SampleList()

	def add(self, groupname, samplename, fname):
		if groupname not in self._samplelist.groups:
			g = SampleGroup(groupname, params.colors[samplename])
			self._samplelist.addGroup(g)

		# Create the sample
		if samplename in params.xs:
			xs = params.xs[samplename]
		else:
			logging.warning('Notice: cross section fallback to group (g: %s, s: %s)', groupname, samplename)
			xs = params.xs[groupname]
		s = MCSample(fname, xs, samplename, directory=self._directory)
		self._samplelist.groups[groupname].add(s)

	def getSampleList(self):
		return self._samplelist


# Data and MC samples are handled by the following classes:
class Sample(object):
	def __init__(self):
		pass

class SingleSample(Sample):
	"""Class representing a single sample.

	This class read the TTrees from a .root file and provide easy access
	to them. It uses TTree.AddFriend() to create a single TTree object
	(Sample.tree) that can be used to access all variables in the .root
	file.

	"""
	def __init__(self, fname, name=None, directory=None):
		self.fname = fname
		self.directory = directory
		self.name = name
		self.disabled_weights = []

		self._openTree()

	def __repr__(self):
		return self.fname

	@staticmethod
	def fromOther(other):
		new = Sample(other.fname, name=other.name, directory=other.directory)
		return new

	def _openTree(self):
		fpath = (self.directory+'/' if self.directory is not None else '') + self.fname
		logging.debug('Opening file: `%s`', fpath)
		self.tfile = ROOT.TFile(fpath, "READ")
		self.branches = []
		if self.tfile.IsZombie():
			raise IOError('Error: file `%s` not found!'%fpath)

		# We'll load all the trees
		keys = [x.GetName() for x in self.tfile.GetListOfKeys()]
		tree_names = filter(lambda x: x.startswith("trees"), keys)
		trees = [self.tfile.Get(k).Get("eventTree") for k in tree_names]
		self.branches += [br.GetName() for br in trees[0].GetListOfBranches()]
		for t in trees[1:]:
			trees[0].AddFriend(t)
			self.branches += [br.GetName() for br in t.GetListOfBranches()]
		self.tree = trees[0]


		#caching stuff
		self.tree.SetCacheSize(10**8)
		self.tree.AddBranchToCache("*")
		for tree in trees:
			tree.SetCacheSize(10**8)
			tree.AddBranchToCache("*")
		ROOT.gEnv.SetValue("TFile.AsyncPrefetching", 1)

	def getTotalEvents(self):
		return self.tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)

	def __str__(self):
		return self.name

class MultiSample(Sample):
	def __init__(self, fname, name=None, directory=None):
		self.name = name if name is not None else fname
		self.logger = logging.getLogger(self.name)
		self.fname = fname
		self.directory = directory
		self.disabled_weights = []
		self.entryListCache = dict()
		self.frac_entries = 1.0
		self.timestats = []
		self._openTree()

	def __getstate__(self):
		d = dict(self.__dict__)
		del d['logger']
		del d['entryListCache']
		return d

	def __setstate__(self, d):
		self.__dict__.update(d)
		self.logger = logging.getLogger(self.name)

	def branches(self):
		return [br.GetName() for br in self.tree.GetListOfBranches()]

	def _switchBranchesOn(self, vars_to_switch):
		self.tree.SetBranchStatus("*", 0)
		self.logger.debug("Switching variables on: %s" % vars_to_switch)
		for var in vars_to_switch:
			self.tree.SetBranchStatus(var, 1)
		return

	def cacheEntryList(self, cut):
		self._switchBranchesOn(cut.getUsedVariables())
		self.tree.SetEntryList(0)
		self.tree.SetProof(False)
		if cut.cutStr not in self.entryListCache.keys():
			self.logger.info("Caching entry list with cut %s" % (cut))
			entry_list_name = "%s_%s" % (self.name, adler32(cut.cutStr))
			ROOT.gROOT.cd()
			if self.tree.GetEntries()==0 or self.frac_entries==0:
				self.logger.warning("Requested entry list over 0 entries, skipping")
				return 0
			self.tree.Draw(">>%s" % entry_list_name, cut.cutStr, "entrylist", int(self.tree.GetEntries()*self.frac_entries))
			elist = ROOT.gROOT.Get(entry_list_name)
			if not elist or elist is None or elist.GetN()==-1:
				raise Exception("Failed to get entry list")
			if elist.GetN()==0:
				self.logger.warning("Entry list was empty")
			self.entryListCache[cut.cutStr] = elist
			self.tree.SetEntryList(elist)
		else:
			self.logger.debug("Loading entry list from cache: %s" % (cut))
			elist = self.entryListCache[cut.cutStr]
			self.tree.SetEntryList(elist)
		self.logger.debug("Cut result: %d events" % elist.GetN())
		return elist.GetN()

	def getColumn(self, var, cut, dtype="f"):
		self.logger.info("Getting column %s" % var)

		self.cacheEntryList(cut)
		self._switchBranchesOn([var.var])
		N = self.tree.Draw(var.var, "", "goff")
		if N <= 0:
			raise Exception("Could not get column")
		buf = self.tree.GetV1()
		arr = ROOT.TArrayD(N, buf)
		self.logger.debug("Column retrieved, copying to numpy array")
		out = numpy.copy(numpy.frombuffer(arr.GetArray(), count=arr.GetSize(), dtype=dtype))
		return out



	def drawHist(self, hist_name, plot_params, cut=None, proof=None):
		t0 = time.time()
		hist_name += "_" + self.name
		self.logger.info("Drawing histogram %s" % hist_name)
		if self.tree.GetEntries()==0:
			self.logger.warning("Tree %s was empty!" % self.tree.GetName())
			ROOT.gROOT.cd()
			hist = ROOT.TH1F(hist_name, hist_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
			return 0, hist
			#raise EmptyTreeException("%s.GetEntries()==0" % self.tree.GetName())
		if cut is None:
			cut = plotfw.params.Cuts.inital

		n_cut = self.cacheEntryList(cut)
		self._switchBranchesOn(plot_params.var.getRelevantBranches())

		if proof:
			self.logger.debug("Output will be in ROOT.TProof instance %s" % str(proof))
			self.tree.SetProof(True)
		else:
			self.tree.SetProof(False)
			ROOT.gROOT.cd()

		draw_cmd = "%s >> %s(%d, %d, %d)" % (plot_params.var.var, hist_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
		weight_str = plot_params.getWeightStr(disabled_weights=self.disabled_weights)
		cutweight_str = "(" + weight_str + ")*(" + cut.cutStr + ")"
		self.logger.debug("Calling TChain.Draw(%s, %s)" % (draw_cmd, weight_str))
		N = self.tree.Draw(draw_cmd, weight_str, "goff")
		self.logger.debug("Histogram drawn with %d entries" % N)
		if int(N) == -1 or n_cut != N:
			raise Exception("Failed to draw histogram: cut result %d but histogram drawn with %d entries" % (N, n_cut))
		if proof:
			hist = proof.GetOutputList().FindObject(hist_name)
		else:
			hist = ROOT.gROOT.Get(hist_name)
		if not hist:
			raise Exception("Failed to get histogram")
		ROOT.gROOT.cd()
		clone_hist = ROOT.TH1F(hist)#hist.Clone(hist_name)
		clone_hist.Sumw2()
		if clone_hist.Integral()==0:
			self.logger.warning("Histogram was empty")
			#raise Exception("Histogram was empty")
		t1 = time.time()
		ts = TreeStats(self.tree.GetEntries(), N, t1-t0)
		self.timestats.append(ts)
		logging.info("Drawing stats: %s" % ts)
		return N, clone_hist

	def _openTree(self):
		fpath = (self.directory+'/' if self.directory is not None else '') + self.fname + '/res/*.root'
		self.logger.debug('Opening file: `%s`', fpath)
		files = glob.glob(fpath)
		self.event_chain = ROOT.TChain(self.name + "_Events", self.name)
		self.lumi_chain = ROOT.TChain(self.name + "_Lumi", self.name)
		if len(files)==0:
			raise Exception("File list is empty")

		self.tfile = files[0]
		for fi in files:
			self.event_chain.AddFile(fi + "/Events")
			self.lumi_chain.AddFile(fi + "/LuminosityBlocks")

		#caching stuff
		self.event_chain.SetCacheSize(100*1024*1024)
		self.event_chain.AddBranchToCache("*", True)
		ROOT.gEnv.SetValue("TFile.AsyncPrefetching", 1)
		self.tree = self.event_chain

	def getTotalEvents(self):
		tot = 0
		n_drawn = self.lumi_chain.Draw("edmMergeableCounter_PATTotalEventsProcessedCount__PAT.product().value >> htemp", "", "goff")
		arr = ROOT.TArrayD(n_drawn, self.lumi_chain.GetV1())
		tot = float(arr.GetSum())
		return tot

	def __str__(self):
		return self.name

class MCSample(MultiSample):
	"""Sample with a cross section."""
	def __init__(self, fname, xs=None, name=None, directory=None):
		super(MCSample,self).__init__(fname, name=name, directory=directory)
		self.xs = float(xs) if xs is not None else plotfw.cross_sections.xs[self.name]

	def scaleToLumi(self, hist, lumi):
		# MC scaling to xs
		expected_events = self.xs * lumi
		total_events = self.getTotalEvents()
		scale_factor = float(expected_events)/float(total_events)
		hist.Scale(scale_factor)

	def drawHist(self, *args, **kwargs):
		lumi = kwargs.pop("lumi") if "lumi" in kwargs.keys() else None
		N, hist = super(MCSample, self).drawHist(*args, **kwargs)
		if lumi is not None:
			self.scaleToLumi(hist, lumi)
		return N, hist

class DataSample(MultiSample):
	"""Sample with a corresponding luminosity"""
	def __init__(self, fname, lumi, name=None, directory=None):
		#super(DataSample,self).__init__(fname, name=name if name is not None else fname, directory=directory)
		super(DataSample,self).__init__(fname, name=name, directory=directory)
		self.luminosity = float(lumi)

# Group of samples with the same color and label
class SampleGroup:
	"""Group of samples with the same color and label

	Useful to, for example, group samples in a stacked histogram.

	"""
	def __init__(self, name, color, pretty_name=None, samples=None):
		self.name = name
		self.color = color
		self.pretty_name = pretty_name if pretty_name is not None else name
		self.samples = samples if samples is not None else []

	@staticmethod
	def fromList(samples):
		return [SampleGroup(s.name, params.colors[s.name], samples=[s]) for s in samples]

	def add(self, s):
		self.samples.append(s)

	def getNames(self):
		return [x.name for x in self.samples]

	def addList(self, sl):
		for sample in sl:
			self.add(sample)

	def getName(self):
		return self.name

	def getLabel(self):
		return self.name

	def getColor(self):
		return self.color

	def getSamples(self):
		return self.samples

	def __str__(self):
		return "{0}: (".format(self.name) + ", ".join(map(str, self.samples)) + ")"

	def __add__(self, other):
		if not isinstance(other, SampleGroup):
			raise TypeError("Can't add instance of type %s to SampleGroup" % str(type(other)))
		out = SampleGroup(self.name, self.color, self.pretty_name)
		for sample in self.samples + other.samples:
			if sample.name in out.getNames():
				raise ValueError("Sample %s is already in group" % str(sample))
			out.add(sample)
		return out

class SampleList:
	"""List of all sample groups"""
	def __init__(self):
		self.groups = {} # initially there are no sample groups

	def addGroup(self, g):
		self.groups[g.getName()] = g

	def addGroups(self, groups):
		map(self.addGroup, groups)

	#def addSample(self, gn, s):
	#	self.groups[gn].add(s)

	def listSamples(self):
		for gk in self.groups:
			print gk
			g = self.groups[gk]
			for s in g.samples:
				print '> ', s

	def getSamples(self):
		samples = []
		for gk in self.groups:
			samples += self.groups[gk].getSamples()
		return samples

	def __str__(self):
		return ", ".join(map(str, self.groups.values()))

	def __add__(self, other):
		if not isinstance(other, SampleList):
			raise TypeError("Can't add object of type %s to SampleList" % str(type(other)))
		out = SampleList()
		for name, group in self.groups:
			out.addGroup(group)
		for name, group in other.groups:
			if name in self.groups.keys():
				raise KeyError("Group %s is already in SampleList" % name)
			out.addGroup(group)
		return out


# Plot parameters
class PlotParams(object):
	"""
	Class that holds the information of what and how to plot.
	var - the variable to plot (type Var)
	r - a tuple with (lower, upper) range for the plot
	"""

	def __init__(self, var, r,
		bins=20, name=None, plotTitle=None, doLogY=False, ofname=None, weights=None,
		x_label=None, vars_to_enable=None, normalize_to="lumi", ymax=None):
		self.var = var
		self.r = r; self.hmin = r[0]; self.hmax = r[1]
		self.bins=bins; self.hbins = bins
		self.plotTitle=plotTitle
		if self.plotTitle is None:
			self.plotTitle = self.var.name
		self._name = name if name is not None else filter_alnum(self.getVarStr())
		self.doLogY = doLogY
		self._ofname = ofname
		if isinstance(weights, types.ListType) and not isinstance(weights, types.StringTypes):
			self.weights = weights
		elif isinstance(weights, types.StringTypes):
			self.weights = [weights]
		else:
			self.weights = None
		self.x_label = x_label if x_label is not None else self.var.name + " [" + self.var.units + "]"
		if vars_to_enable is None:
			self.vars_to_enable = [parent_branch(self.getVarStr())]
		else:
			self.vars_to_enable = vars_to_enable

		self.do_chi2 = False
		self.normalize_to = normalize_to
		self.stat_opts = None

		self._ymax = ymax

	def getVarStr(self):
		return self.var.var

	def getWeightStr(self, disabled_weights=[]):
		if self.weights is None:
			return "1.0"
		else:
			weights = list(set(self.weights).difference(set(disabled_weights)))
			return "*".join(weights)

	def putStats(self):
		self.stat_opts = "legend"

	def doChi2Test(self, group_a_name, group_b_name, chi2options=None):
		self.do_chi2 = True
		self.chi2_a = group_a_name
		self.chi2_b = group_b_name
		self.chi2options = chi2options

	def getVars(self):
		vars_to_switch = []
		vars_to_switch += self.vars_to_enable
		if self.weights is not None:
			vars_to_switch += self.weights

		vars_to_switch = [parent_branch(v) for v in vars_to_switch]
		return vars_to_switch


	def __repr__(self):
		return "PlotParams: {0} in range {1} with weights {2}".format(self.var, self.r, self.weights)

	def getName(self):
		#return filter_alnum(self._name)
		return self._name
