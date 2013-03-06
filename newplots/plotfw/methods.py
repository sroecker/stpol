import ROOT
import string
import types
import params
import logging

from plotfw.params import Cut # FIXME: temporary hack for backwards comp.

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
		self.tfile = ROOT.TFile(fpath)
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

		#self.perfstats = ROOT.TTreePerfStats(self.name, self.tree)

	def getTotalEvents(self):
		return self.tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)

	def __str__(self):
		return self.name

class MCSample(Sample):
	"""Sample with a cross section."""
	def __init__(self, fname, xs, name=None, directory=None):
		super(MCSample,self).__init__(fname, name=name, directory=directory)
		self.xs = float(xs)

class DataSample(Sample):
	"""Sample with a corresponding luminosity"""
	def __init__(self, fname, lumi, name=None, directory=None):
		super(DataSample,self).__init__(fname, name=name if name is not None else fname, directory=directory)
		self.luminosity = float(lumi)

# Group of samples with the same color and label
class SampleGroup:
	"""Group of samples with the same color and label

	Useful to, for example, group samples in a stacked histogram.

	"""
	def __init__(self, name, color, pretty_name=None):
		self.name = name
		self.color = color
		self.pretty_name = pretty_name if pretty_name is not None else name
		self.samples = [] # initially there are no samples

	def add(self, s):
		self.samples.append(s)

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

class SampleList:
	"""List of all sample groups"""
	def __init__(self):
		self.groups = {} # initially there are no sample groups

	def addGroup(self, g):
		self.groups[g.getName()] = g

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

# Plot parameters
class PlotParams(object):
	"""Class that holds the information of what and how to plot."""
	def __init__(self, var, r, bins=20, name=None, plotTitle=None, doLogY=False, ofname=None, weights=None, x_label=None, vars_to_enable=None):
		self.var = var
		self.r = r; self.hmin = r[0]; self.hmax = r[1]
		self.bins=bins; self.hbins = bins
		self.plotTitle=plotTitle
		if self.plotTitle is None:
			self.plotTitle = self.var
		self._name = name if name is not None else filter_alnum(var)
		self.doLogY = doLogY
		self._ofname = ofname
		if isinstance(weights, types.ListType) and not isinstance(weights, types.StringTypes):
			self.weights = weights
		elif isinstance(weights, types.StringTypes):
			self.weights = [weights]
		else:
			self.weights = None
		self.x_label = self.var if x_label is None else x_label
		if vars_to_enable is None:
			self.vars_to_enable = [var]
		else:
			self.vars_to_enable = vars_to_enable

		self.do_chi2 = False

	def getWeightStr(self, disabled_weights=[]):
		if self.weights is None:
			return "1.0"
		else:
			weights = list(set(self.weights).difference(set(disabled_weights)))
			return "*".join(weights)

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
		return vars_to_switch


	def __repr__(self):
		return "{0} in range {1} with weights {2}".format(self.var, self.r, self.weights)

	def getName(self):
		#return filter_alnum(self._name)
		return self._name
