import ROOT
import string
import types
import params
import logging
import glob
import numpy
import pdb
import time
import multiprocessing
import fnmatch
import types

from plotfw.histogram import Histogram
from plotfw.params import Cut # FIXME: temporary hack for backwards comp.
from plotfw.params import Var # FIXME: temporary hack for backwards comp.
from plotfw.params import parent_branch
import plotfw.cross_sections
import copy

def chksm(s):
	"""Finds a checksum of a string

	Uses zlib's adler32 internally. The value will always be a positive
	integer.
	"""
	import zlib
	return zlib.adler32(str(s)) + 2**31

class EntryListException(Exception):
	pass

def mp_SampleGroup_drawHists(args):
	(group, arg_list, kwarg_list) = args
	logger = logging.getLogger(__name__ + "_" + multiprocessing.current_process().name + "_" + group.name)
	logger.debug("Started multiprocessing draw on one group")
	hist = group.drawHists(*arg_list, **kwarg_list)
	logger.debug("Done multiprocessing draw on one group")
	return (group, hist)

def mp_Sample_drawHist(args):
	(sample, arg_list, kwarg_list) = args
	logger = logging.getLogger(__name__ + "_" + multiprocessing.current_process().name + "_" + sample.name)
	logger.debug("Started multiprocessing draw on one sample")
	n_filled, sample_hist = sample.drawHist(*arg_list, **kwarg_list)
	logger.debug("Done multiprocessing draw one sample")
	sample_hist.calc_int_err()
	return (sample, sample_hist)


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
		self.logger = logging.getLogger(self.name + "_" + multiprocessing.current_process().name)
		self.fname = fname
		self.directory = directory
		self.disabled_weights = []
		self.entryListCache = dict()
		self.frac_entries = 1.0
		self.timestats = []
		self.total_events = None
		self._openTree()

	def close(self):
		del self.event_chain
		del self.lumi_chain

	def __getstate__(self):
		d = dict(self.__dict__)
		del d['logger']
		del d['tree']
		#del d['entryListCache']
		return d

	def __setstate__(self, d):
		self.__dict__.update(d)
		self.logger = logging.getLogger(self.name + "_" + multiprocessing.current_process().name)
		self._openTree()
		#self.entryListCache = dict()

	def branches(self):
		return [br.GetName() for br in self.tree.GetListOfBranches()]

	def _switchBranchesOn(self, vars_to_switch):
		self.tree.SetBranchStatus("*", 0)
		self.lumi_chain.SetBranchStatus("*", 0)
		self.logger.debug("Switching variables on: %s" % vars_to_switch)
		for var in vars_to_switch:
			if isinstance(var, Var):
				self.tree.SetBranchStatus(var.var, 1)
			elif isinstance(var, types.StringType):
				self.tree.SetBranchStatus(var, 1)
			else:
				raise TypeError("Var type not recognized")
		return

	def cacheEntryList(self, cut, frac_entries=None):
		t0 = time.time()
		self._switchBranchesOn(cut.getUsedVariables())
		self.tree.SetEntryList(0)
		self.tree.SetProof(False)
		if not frac_entries:
			frac_entries = 1.0
		N_lines = int(self.tree.GetEntries()*frac_entries)
		if cut.cutStr not in self.entryListCache.keys():
			self.logger.info("Caching entry list with cut %s over %d entries" % (cut, N_lines))
			entry_list_name = "%s_%s" % (self.name, chksm(cut.cutStr))
			ROOT.gROOT.cd()
			if self.tree.GetEntries()==0 or self.frac_entries==0:
				self.logger.warning("Requested entry list over 0 entries, skipping")
				return 0
			self.tree.Draw(">>%s" % entry_list_name, cut.cutStr, "entrylist", N_lines)
			elist = ROOT.gROOT.Get(entry_list_name)
			if not elist or elist is None or elist.GetN()==-1:
				raise EntryListException("Failed to get entry list: %s" % elist)
			if elist.GetN()==0:
				self.logger.warning("Entry list was empty")

			self.entryListCache[cut.cutStr] = elist
			self.tree.SetEntryList(elist)
		else:
			self.logger.debug("Loading entry list from cache: %s" % (cut))
			elist = self.entryListCache[cut.cutStr]
			self.tree.SetEntryList(elist)
		t1 = time.time()
		dt = t1-t0
		#ts = TreeStats(self.tree.GetEntries(), N, t1-t0)
		#self.timestats.append(ts)
		self.logger.debug("Caching entry list took %.2f seconds, %.2f events/second" % (dt, float(N_lines)/dt))
		self.logger.debug("Cut result: %d events" % elist.GetN())
		return elist.GetN()

	def getColumn(self, var, cut, dtype="float64", frac_entries=None):
		self.logger.info("Getting column %s" % var)

		self.cacheEntryList(cut, frac_entries=frac_entries)
		self._switchBranchesOn([var.var])
		N = self.tree.Draw(var.var, "", "goff")
		if N <= 0:
			raise Exception("Could not get column")
		buf = self.tree.GetV1()
		arr = ROOT.TArrayD(N, buf)
		self.logger.debug("Column retrieved, copying to numpy array")
		out = numpy.copy(numpy.frombuffer(arr.GetArray(), count=arr.GetSize()))
		return out



	"""
	Draws a histogram fro the sample with base name 'hist_name'.
	hist_name - a string containing the base name of the histogram, the sample name will be added
	plot_params - a PlotParams type object with the var and weights
	cut - an optional Cut type object specifying the cut
	proof - an optional instance of TProof type for multicore use
	maxLines - specify the maximum number of TTree lines to iterate over when drawing. None=all lines
	"""
	def drawHist(self, hist_name, plot_params, cut=None, frac_entries=None):
		if not isinstance(plot_params, PlotParams):
			raise TypeError("plot_params has wrong type")

		t0 = time.time()
		hist_name += "_" + self.name
		self.logger.info("Drawing histogram %s" % hist_name)
		if self.tree.GetEntries()==0:
			self.logger.warning("Tree %s was empty!" % self.tree.GetName())
			ROOT.gROOT.cd()
			hist = Histogram(hist_name, hist_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
			return 0, hist
			#raise EmptyTreeException("%s.GetEntries()==0" % self.tree.GetName())
		if cut is None:
			cut = plotfw.params.Cuts.inital

		n_cut = self.cacheEntryList(cut, frac_entries=frac_entries)
		self._switchBranchesOn(plot_params.var.getUsedVariables() + plot_params.getUsedWeights(disabled_weights=self.disabled_weights))

		#if proof:
		#	self.logger.debug("Output will be in ROOT.TProof instance %s" % str(proof))
		#	self.tree.SetProof(True)
		#else:
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
		#if proof:
		#	hist = proof.GetOutputList().FindObject(hist_name)
		#else:
		hist = ROOT.gROOT.Get(hist_name)
		if not hist:
			raise Exception("Failed to get histogram")

		#Make a copy into ROOT global memory directory (sigh)
		ROOT.gROOT.cd()
		clone_hist = Histogram(hist)#hist.Clone(hist_name)

		clone_hist.Sumw2()
		if clone_hist.Integral()==0:
			self.logger.warning("Histogram was empty")
			#raise Exception("Histogram was empty")
		t1 = time.time()
		if not frac_entries:
			frac_entries=1.0
		ts = TreeStats(frac_entries*self.tree.GetEntries(), N, t1-t0)
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
			raise Exception("File list is empty for %s" % self.name)

		self.tfile = files[0]
		for fi in files:
			self.event_chain.AddFile(fi + "/Events")
			self.lumi_chain.AddFile(fi + "/LuminosityBlocks")

		#caching stuff
		self.event_chain.SetCacheSize(100*1024*1024)
		self.event_chain.AddBranchToCache("*", True)
		self.lumi_chain.SetCacheSize(100*1024*1024)
		ROOT.gEnv.SetValue("TFile.AsyncPrefetching", 1)
		self.tree = self.event_chain
		self.logger.debug('Done opening file and creating caches.')

	def getTotalEvents(self):
		tot = 0
		if self.total_events is None:
			self.logger.debug("Caching total PAT processed event count")
			self.lumi_chain.AddBranchToCache("edmMergeableCounter_PATTotalEventsProcessedCount__PAT.*", True)
			self.lumi_chain.SetBranchStatus("*", 0)
			self.event_chain.SetBranchStatus("*", 0)
			self.lumi_chain.SetBranchStatus("edmMergeableCounter_PATTotalEventsProcessedCount__PAT.*", 1)
			n_drawn = self.lumi_chain.Draw("edmMergeableCounter_PATTotalEventsProcessedCount__PAT.obj.value >> htemp", "", "goff")
			self.logger.debug("Event count histo drawn, getting array sum")
			arr = ROOT.TArrayD(n_drawn, self.lumi_chain.GetV1())
			tot = float(arr.GetSum())
			del arr
			self.total_events = tot
		self.logger.info("Total events = %d" % self.total_events)
		return self.total_events

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
		self.disabled_weights = ["*"]

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
		self.logger = logging.getLogger(self.name + "_" + multiprocessing.current_process().name)

	def __getstate__(self):
		d = dict(self.__dict__)
		del d['logger']
		return d

	def __setstate__(self, d):
		self.__dict__.update(d)
		self.logger = logging.getLogger(self.name + "_" + multiprocessing.current_process().name)

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

	def drawHists(self, *args, **kwargs):
		n_cores = kwargs.pop("n_cores") if "n_cores" in kwargs.keys() else None
		args = list(args)
		hist_name = args[0] + "_" + self.name
		args[0] = hist_name
		plot_params = args[1]

		n_samples = len(self.getSamples())
		arg_list = zip(self.getSamples(), n_samples*[args], n_samples*[kwargs])
		if n_cores is None:
			res = map(mp_Sample_drawHist, arg_list)
		else:
			pool = multiprocessing.Pool(n_samples if n_cores<=0 else n_cores)
			res = pool.map(mp_Sample_drawHist, arg_list)

		hist = Histogram(hist_name, self.pretty_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
		hist.SetLineColor(self.color)
		hist.SetLineWidth(3)

		for sample, sample_hist in res:
			hist.Add(sample_hist)

#		for sample in self.samples:
#			sample.close()
#			del sample
#
		self.samples = [x[0] for x in res]
		if plot_params.normalize_to == "unity":
			hist_integral = hist.Integral()
			self.logger.debug('Hist `%s` integral: %f' % (hist_name, hist_integral))
			if hist_integral>0:
				hist.Scale(1.0/hist_integral)
				self.logger.debug('Hist `%s` integral: %f (after scaling)' % (hist_name, hist.Integral()))
			else:
				self.logger.warning("Histogram {0} was empty".format(hist))
				hist.Scale(0)
		hist.calc_int_err()
		return hist

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

	def drawHists(self, *args, **kwargs):
		n_cores = kwargs.pop("n_cores") if "n_cores" in kwargs.keys() else None
		group_list = self.groups.values()
		many_args = zip(group_list, [args]*len(group_list), [kwargs]*len(group_list))
		if n_cores is None:
			ret = map(mp_SampleGroup_drawHists, many_args)
		else:
			if n_cores <= 0:
				pool = multiprocessing.Pool(len(group_list))
			else:
				pool = multiprocessing.Pool(n_cores)
			ret = pool.map(mp_SampleGroup_drawHists, many_args)
		groups = [x[0] for x in ret]
		self.groups = {}
		for group in groups:
			self.groups[group.name] = group
		return [(x[0].name, Histogram(x[1])) for x in ret]


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
		if isinstance(weights, types.ListType):
			self.weights = weights
		elif isinstance(weights, params.Var):
			self.weights = [weights]
		elif not weights:
			self.weights = None
		else:
			raise TypeError("Unsuitable type for weights: %s" % weights)
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

	"""
	disabled_weights is a list of strings containing the wildcard matches of the weights to be disabled
	"""

	def getUsedWeights(self, disabled_weights=[]):
		if self.weights is None:
			return []
		else:
			disabled_weight_matches = []
			for dw in disabled_weights:
				matching_weights = [w for w in self.weights if fnmatch.fnmatch(w.var, dw)]
				disabled_weight_matches += matching_weights
			var_list = [w for w in list(set(self.weights).difference(set(disabled_weight_matches)))]
			return var_list

	def getWeightStr(self, disabled_weights=[]):
		weight_vars = [w.var for w in self.getUsedWeights(disabled_weights)]
		if len(weight_vars)>0:
			return "*".join(weight_vars)
		else:
			return "1.0"
	def putStats(self):
		self.stat_opts = "legend"

	def doChi2Test(self, group_a_name, group_b_name, chi2options=None):
		self.do_chi2 = True
		self.chi2_a = group_a_name
		self.chi2_b = group_b_name
		self.chi2options = chi2options

	def getBranches(self):
		vars_to_switch = []
		vars_to_switch += self.vars_to_enable
		if self.weights is not None:
			for w in self.weights:
				vars_to_switch += w.var

		vars_to_switch = [parent_branch(v) for v in vars_to_switch]
		return vars_to_switch


	def __repr__(self):
		return "PlotParams: {0} in range {1} with weights {2}".format(self.var, self.r, self.weights)

	def getName(self):
		#return filter_alnum(self._name)
		return self._name
