import autoLoad
import ROOT
import logging, time
import random
import string
import methods,params,plotlog
from methods import Sample, MCSample, DataSample, SampleGroup, SampleList
from methods import PlotParams, SampleListGenerator
from methods import EmptyTreeException
from histogram import Histogram
import cPickle as pickle
import multiprocessing
import pdb
import math
from odict import OrderedDict as dict

text_size = 0.025

logger = logging.getLogger(__name__)

def getProofOutput(proof, name):
	return proof.GetOutputList().FindObject(name)

def mp_applyCut(s):
	return PlotCreator._applyCut(s[0], s[1], s[2], s[3], s[4])

def drawSample(args):
	logger.debug("Started multiprocessing draw on worker %s" % multiprocessing.current_process().name)
	(sample, hist_name, plot_params, cut, frac_entries) = args
	n_filled, sample_hist = sample.drawHist(hist_name, plot_params, cut=cut, proof=None, maxLines=sample.tree.GetEntries()*frac_entries)
	logger.debug("Done multiprocessing draw on worker %s " % multiprocessing.current_process().name)
	return (sample.name, n_filled, pickle.dumps(sample_hist))


class PlotCreator(object):
	def __init__(self, frac = 1.0, n_cores=10):
		self.frac_entries = frac
		self.samples = None
		self.maxLines=None
		self.proof = None
		self.set_n_cores(n_cores)

	@staticmethod
	def _uniqueCutStr(cut_str, weight_str):
		"""
		Returns a unique hash for the plot_params.weight*cut_str object
		"""
		uniq = methods.chksm("({0})*({1})".format(weight_str, cut_str))
		return uniq

	def set_n_cores(self, n_cores):
		self.n_cores = n_cores

		#Run either python multiprocessing or PROOF
		self.run_multicore = self.n_cores > 1 and not self.proof
		if self.run_multicore:
			logger.info("Switching to multicore mode: n_cores=%d" % self.n_cores)
		else:
			logger.info("Switching to single core mode")



	def _applyCut(self, cutstr, sample, reset=True, frac_entries=1, multicore=True):
		"""
		Apply the cut 'cutstr' on sample 's'. Optionally reset the tree event list
		before cutting and process only a limited number of entries.
		"""

		if self.proof is not None:
			raise Exception("Using event list with PROOF does not work")

		t_cut = time.time()
		logger.debug('Cutting on `%s`', sample.name)

		#if logger.getEffectiveLevel()==logging.DEBUG:
		#   perfstats = ROOT.TTreePerfStats(sample.name, sample.tree)

		if reset:
			sample.tree.SetEventList(0)

		logger.debug("Drawing event list for sample {0}".format(sample.name))
		uniqueName = sample.name + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))

		elist_name = "elist_"+uniqueName
		cut = ROOT.TCut(cutstr)
		ROOT.gROOT.cd()
		nEvents = sample.tree.Draw(">>%s"%elist_name, cutstr)#, 'entrylist', int(float(sample.tree.GetEntries())*frac_entries))
		logger.debug("Done drawing {0} events into list {1}".format(nEvents, elist_name))
		elist = ROOT.gROOT.Get(elist_name)
		if not elist:
			raise Exception("Failed to get event list")
		sample.tree.SetEventList(elist)

		#retList = pickle.dumps(elist)
		#logger.debug('Cutting on `%s` took %f', tempSample.name, time.time() - t_cut)

		#if logger.getEffectiveLevel()==logging.DEBUG:
		#   perfstats.SaveAs("perf_" + str(methods.chksm(tempSample.name + cutstr)) + ".root")

		#del tempSample
		return elist

	def _applyCuts(self, cutstr, smpls, reset=True):
		t_cut = time.time()

		for sample in smpls:
			self._applyCut(cutstr, sample)

		logger.info('Cutting on all took %f', time.time()-t_cut)

	def plot(self, cut, plots, cutDescription=""):
		"""Method takes a cut and list of plots and then returns a list plot objects."""

		t0 = time.time()
		# Apply cuts
		self._cutstr = cut.cutStr
		logger.info("Plotting samples {0} with Cut({1}), plots: {2}".format(self.samples, cut, plots))
		logger.debug('Cut string: %s', self._cutstr)

		smpls = self.samples.getSamples()

	#   if self.proof is None:
	#	   #self._switchBranchesOn(cut._vars)
	#	   self._applyCuts(self._cutstr, smpls)

		retplots = [self._plot(x, cut) for x in plots]

		for p in retplots:
			p.setPlotTitle(cutDescription)

		t1 = time.time()
		logger.info("Plotting took {0:.1f} seconds".format(t1-t0))

		return retplots

class StackPlotCreator(PlotCreator):
	"""Class that is used to create stacked plots

	Initalizer takes the data and MC samples which are then plotted.
	datasamples is either of type DataSample, [DataSample] or SampleGroup.
	mcsamples has to be of type SampleList

	"""
	def __init__(self, datasamples, mcsamples):
		super(StackPlotCreator, self).__init__()
		self._mcs = mcsamples

		# if a single data sample is given it does not have to be a list
		if isinstance(datasamples, SampleGroup):
			self._data = datasamples
		elif isinstance(datasamples, list):
			self._data = SampleGroup('data', ROOT.kBlack)
			map(self._data.add, datasamples)
		elif isinstance(datasamples, DataSample):
			self._data = SampleGroup('data', ROOT.kBlack)
			self._data.add(datasamples)
		else:
			raise TypeError('Bad type for `datasamples`!')

		self.samples = SampleList()
		for group in self._mcs.groups.values():
			self.samples.addGroup(group)
		self.samples.addGroup(self._data)

	def getSamples(self):
		return self._mcs.getSamples() + self._data.getSamples()

	def _plot(self, plot_params, cut):
		"""Internally used plotting method.

		It takes a PlotParams class and returns the corresponding Plot
		object.

		"""
		unique_id = PlotCreator._uniqueCutStr(self._cutstr, plot_params.getWeightStr())

		plotname = 'plot_cut%s_%s' % (unique_id, plot_params.getName())
		logger.info('Plotting: %s', plotname)

		plot = StackPlot(plot_params, self.samples, unique_id)
		plot.log.addParam('Variable', plot_params.getVarStr())
		plot.log.addParam('HT min', plot_params.hmin)
		plot.log.addParam('HT max', plot_params.hmax)
		plot.log.addParam('HT bins', plot_params.hbins)

		plot.log.setCuts([''], self._cutstr)

		# Create log variables
		plot.log.addVariable('filled', 'Events filled')
		plot.log.addVariable('int', 'Integrated events')

		# Create data histogram
		total_luminosity = 0.0
		data_hist_name = '%s_hist_data'%plotname

		plot.data_hist = Histogram(data_hist_name, '', plot_params.hbins, plot_params.hmin, plot_params.hmax)
		plot.data_hist.SetMarkerStyle(20)

		ret = self._data.drawHists(data_hist_name, plot_params, cut, frac_entries=self.frac_entries, n_cores=self.n_cores)
		plot.data_hist.Add(ret)

		total_luminosity = sum([sample.luminosity for sample in self._data.samples])
		#for sample in self._data.getSamples():
		#	if not isinstance(sample, DataSample):
		#		raise TypeError("Sample %s is not data" % str(sample))
		#	#for data there is no weight necessary
		#	dt_filled, data_hist = sample.drawHist(data_hist_name, plot_params, cut=cut, proof=self.proof, maxLines=sample.tree.GetEntries()*self.frac_entries)

		#	total_luminosity += sample.luminosity
		#	dname = sample.name
		#	plot.log.addProcess(dname, ismc=False)
		#	plot.log.setVariable(dname, 'crsec', sample.luminosity)
		#	plot.log.setVariable(dname, 'fname', sample.fname)
		#	plot.log.setVariable(dname, 'filled', dt_filled)

		#	err = ROOT.Double()
		#	dt_int = data_hist.IntegralAndError(1, data_hist.GetNbinsX(), err)

		#	plot.log.setVariable(dname, 'int', dt_int)
		#	plot.log.setVariable(dname, 'int_err', float(err))

		#	plot.data_hist.Add(data_hist)

		#plot.log.addParam('Luminosity', total_luminosity)
		#plot.log.addParam('Effective luminosity', effective_lumi)

		data_max = plot.data_hist.GetMaximum()
		#plot.log.addParam('Data binmax', data_max)
		plot.data_hist.SetTitle("L_{int.} = %.1f fb^{-1}" % (total_luminosity/1000.0))

		mc_int = 0
		plot.mc_hists = []
		plot.mc_group_hists = dict()
		logger.info("Total luminosity: %f" % total_luminosity)

		ret = self._mcs.drawHists("%s_hist_mc" % plotname, plot_params, cut, self.frac_entries, n_cores=self.n_cores, lumi=total_luminosity)
		for group_name, hist in ret:
			plot.mc_group_hists[group_name] = hist
			plot.mc_hists.append(hist.child_hists)
		#for group_name, group in self._mcs.groups.items():
		#	group_hist_name = 'hist_%s_mc_group_%s'%(plotname, group_name)
		#	mc_group_hist = ROOT.TH1F(group_hist_name, group.pretty_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
		#	mc_group_hist.filled_count = 0
		#	mc_group_hist.Sumw2()
		#	mc_group_hist.SetFillColor(group.color)
		#	mc_group_hist.SetLineColor(group.color)
		#	mc_group_hist.SetLineWidth(0)

		#	for sample in group.samples:
		#		plot.log.addProcess(sample.name)
		#		plot.log.setVariable(sample.name, 'crsec', sample.xs)
		#		plot.log.setVariable(sample.name, 'fname', sample.fname)
		#		hist_name = group_hist_name + "_" + sample.name
		#		mc_filled, mc_hist = sample.drawHist(group_hist_name, plot_params, cut=cut, proof=self.proof, lumi=total_luminosity, maxLines= sample.tree.GetEntries()*self.frac_entries )
		#		mc_hist.filled_count = mc_filled
		#		plot.log.setVariable(sample.name, 'filled', mc_filled)

		#		# MC scaling to xs (Already done by drawHist on an as-need basis)
		#		expected_events = sample.xs * total_luminosity
		#		total_events = sample.getTotalEvents()
		#		scale_factor = float(expected_events)/float(total_events)

		#		plot.mc_hists.append(mc_hist)
		#		mc_group_hist.Add(mc_hist)
		#		mc_group_hist.filled_count += mc_hist.filled_count

		#		err = ROOT.Double()
		#		mc_int = mc_hist.IntegralAndError(1, mc_hist.GetNbinsX(), err)
		#		logger.debug("Histogram integral = %.2f" % mc_int)
		#		plot.log.setVariable(sample.name, 'totev', total_events)
		#		plot.log.setVariable(sample.name, 'expev', expected_events)
		#		plot.log.setVariable(sample.name, 'scf', scale_factor)
		#		plot.log.setVariable(sample.name, 'int', mc_int)
		#		plot.log.setVariable(sample.name, 'int_err', float(err))
		#	plot.mc_group_hists[group_name] = mc_group_hist

		# Kolmorogov test
		total_mc_hist = ROOT.TH1F('hist_mc_ktbase_%s'%plotname, 'MC stat. err.', plot_params.hbins, plot_params.hmin, plot_params.hmax)
		total_mc_hist.SetFillStyle(3004) #show only error band
		total_mc_hist.SetFillColor(ROOT.kBlue+3)
		total_mc_hist.SetLineColor(ROOT.kBlue+3)

		sorted_group_hists = dict()
		for name, val in sorted(plot.mc_group_hists.items(), key=lambda x: x[1].count_events):
			sorted_group_hists[name] = val
		plot.mc_group_hists = sorted_group_hists

		for hist_name, hist in plot.mc_group_hists.items():
			total_mc_hist.Add(hist)

		mc_max = total_mc_hist.GetMaximum()
		plot.log.addParam('MC binmax', mc_max)
		plot.total_mc_hist = total_mc_hist
		plot.log.addParam('Kolmogorov test', plot.data_hist.KolmogorovTest(total_mc_hist))
		plot.log.addParam('Chi2/ndf', plot.data_hist.Chi2Test(total_mc_hist, "UW CHI2/NDF"))

		# Stacking the histograms
		plot_title = '%s (%s)'%(plot_params.getVarStr(), plotname)
		plot.hist_stack = ROOT.THStack('stack_%s'%plotname, plot_title)

		for hist in reversed(plot.mc_group_hists.values()):
			plot.hist_stack.Add(hist)

		plot.legend = BaseLegend(plot)

		ymax = plot_params._ymax if plot_params._ymax is not None else 1.1*max(data_max, mc_max)
		plot.hist_stack.SetMaximum(ymax)

		# return the plot object where it can be drawn etc.
		return plot

class ShapePlotCreator(PlotCreator):
	"""Create plots for sample shape comparison."""
	def __init__(self, samples, **kwargs):
		super(ShapePlotCreator, self).__init__(**kwargs)
		self._slist = samples
		self.samples = self._slist

	def getSamples(self):
		return self._slist.getSamples()

	def _plot(self, plot_params, cut):

		uniq = PlotCreator._uniqueCutStr(cut.cutStr, plot_params.getWeightStr())

		plot = ShapePlot(plot_params, self.samples, unique_id=uniq)
		plotname = 'plot_cut%s_%s' % (uniq, plot_params.getName())
		logger.debug('Plotting: %s', plotname)

		#plot._maxbin = 0.0
		hists = self._slist.drawHists(plotname, plot_params, cut, self.frac_entries, n_cores=self.n_cores)
		for hn, h in hists:
			plot.addHist(h, hn)
#		for group_name, group in self._slist.groups.items():
#			hist_name = 'hist_%s_%s'%(plotname, group.getName())
#
#			hist = ROOT.TH1F(hist_name, group.pretty_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
#			hist.Sumw2()
#			hist.SetStats(False)
#			hist.SetLineColor(group.color)
#			hist.SetLineWidth(3)
#
#			filled_tot = 0.0
#
#			n_samples = len(group.getSamples())
#			args = zip(group.getSamples(), n_samples*[hist_name], n_samples*[plot_params], n_samples*[cut], n_samples*[self.frac_entries])
#			if self.run_multicore:
#				logger.debug("Running over samples with multicore map")
#				p = multiprocessing.Pool(8)
#				res = p.map(drawSample, args)
#				logger.debug("Done running over samples with multicore map")
#			else:
#				logger.debug("Running over samples with single core map")
#				res = map(drawSample, args)
#				logger.debug("Done running over samples with single core map")
#
#			res = map(lambda x: (x[0], x[1], pickle.loads(x[2])), res)
#
#			for sample_name, n_filled, sample_hist in res:
#				plot.log.addProcess(sample_name)
#				#n_filled, sample_hist = sample.drawHist(hist_name, plot_params, cut, self.proof)
#				err = ROOT.Double()
#				integral = sample_hist.IntegralAndError(1, sample_hist.GetNbinsX(), err)
#				plot.log.setVariable(sample_name, 'int', integral)
#				plot.log.setVariable(sample_name, 'int_err', float(err))
#				hist.Add(sample_hist)
#
#			if plot_params.normalize_to == "unity":
#				hist_integral = hist.Integral()
#				logger.debug('Hist `%s` integral: %f' % (hist_name, hist_integral))
#				if hist_integral>0:
#					hist.Scale(1.0/hist_integral)
#					logger.debug('Hist `%s` integral: %f (after scaling)' % (hist_name, hist.Integral()))
#				else:
#					logger.warning("Histogram {0} was empty".format(hist))
#					hist.Scale(0)
#			plot._maxbin = max(plot._maxbin, hist.GetMaximum())
#			plot.addHist(hist, group.name)
#
		plot.legend = BaseLegend(plot)

		return plot

class SeparateCutShapePlotCreator(ShapePlotCreator):
	def __init__(self, samplegroup, cuts, **kwargs):
		super(ShapePlotCreator, self).__init__(**kwargs)
		self._cuts = cuts
		self._samplegroup = samplegroup

	def plot(self, plots):
		"""Method takes a cut and list of plots and then returns a list plot objects."""
		t0 = time.time()
		# Apply cuts
		logger.info("Plotting samples {0}, plots: {1}".format(self.samples, plots))
		retplots = [self._plot(x) for x in plots]
		for p in retplots:
			p.setPlotTitle('????')
		t1 = time.time()
		logger.info("Plotting took {0:.1f} seconds".format(t1-t0))

		return retplots

	def _plot(self, plot_params):
		plot = ShapePlot(plot_params, self._samplegroup, None)
		plotname = 'plot_%s' % (plot_params.getName())
		logger.debug('Plotting: %s', plotname)

		plot._maxbin = 0.0
		
		for cutname,cut in self._cuts.items():
			uniq = PlotCreator._uniqueCutStr(cut.cutStr, plot_params.getWeightStr())
			hist_name = 'hist_%s_%s_%s'%(plotname, cutname, uniq)
			
			hist = ROOT.TH1F(hist_name, '%s_%s'%(plotname,cutname), plot_params.hbins, plot_params.hmin, plot_params.hmax)
			hist.Sumw2()
			hist.SetStats(False)
			hist.SetLineColor(ROOT.kRed)
			hist.SetLineWidth(3)
			
			filled_tot = 0.0
			
			for s in self._samplegroup.getSamples():
				uname = '%s_%s' % (hist_name, s.name)
				logger.debug('uaname: %s', uname)
				n_filled, sample_hist = s.drawHist(uname, plot_params, cut=cut)
				hist.add(sample_hist)
			
			if plot_params.normalize_to == "unity":
				hist_integral = hist.Integral()
				logger.debug('Hist `%s` integral: %f' % (hist_name, hist_integral))
				if hist_integral>0:
					hist.Scale(1.0/hist_integral)
					logger.debug('Hist `%s` integral: %f (after scaling)' % (hist_name, hist.Integral()))
				else:
					logger.warning("Histogram {0} was empty".format(hist))
					hist.Scale(0)
			
			plot._maxbin = hist.GetMaximum()
			plot.addHist(hist, cutname)
		'''
		for group_name, group in self._slist.groups.items():
			hist_name = 'hist_%s_%s'%(plotname, group.getName())

			filled_tot = 0.0

			n_samples = len(group.getSamples())
			args = zip(group.getSamples(), n_samples*[hist_name], n_samples*[plot_params], n_samples*[cut], n_samples*[self.frac_entries])
			if self.run_multicore:
				p = multiprocessing.Pool(8)
				res = p.map(drawSample, args)
			else:
				res = map(drawSample, args)

			res = map(lambda x: (x[0], x[1], pickle.loads(x[2])), res)

			for sample_name, n_filled, sample_hist in res:
				plot.log.addProcess(sample_name)
				#n_filled, sample_hist = sample.drawHist(hist_name, plot_params, cut, self.proof)
				err = ROOT.Double()
				integral = sample_hist.IntegralAndError(1, sample_hist.GetNbinsX(), err)
				plot.log.setVariable(sample_name, 'int', integral)
				plot.log.setVariable(sample_name, 'int_err', float(err))
				hist.Add(sample_hist)
		'''

		plot.legend = BaseLegend(plot)

		return plot

class Plot(object):
	"""This class represents a single plot and has the methods to export it.

	This class puts everything together (different histograms, legend etc)
	and allows to export the plot easily. It also handles the metadata
	logger.

	"""
	def __init__(self, plot_params, sample_list, unique_id):
		self.log = plotlog.PlotLog()
		self._plot_params = plot_params
		self._unique_id = str(unique_id)
		self.sample_list = sample_list
		self.setPlotTitle("")

	def setPlotTitle(self, cutDescription=""):
		self.cutDescription = cutDescription
		self.plotTitle = self._plot_params.plotTitle + " in " + self.cutDescription


	def saveToROOT(self, tfile, objects):
		dirname = self.plotTitle + "_" + self._unique_id
		tfile.mkdir(dirname)
		tfile.cd(dirname)
		for o in objects:
			o = type(o)(o)
			o.Clone()
		tfile.Write()
	def draw(self):
		self.yield_table = YieldTable(self.sample_list, self)
		self.legend.Draw('SAME')
		self.cvs.SetLogy(self._plot_params.doLogY)
		self.yield_table.draw()
		if self._plot_params.do_chi2:
			self.chi2pad = Chi2ValuePad(
				self.getHistogram(self._plot_params.chi2_a),
				self.getHistogram(self._plot_params.chi2_b),
				chi2options=self._plot_params.chi2options
			)
			self.chi2pad.draw()

	def save(self, w=650, h=400, log=False, fmt='png', fout=None, ofdir=None):
		if ofdir is None:
			ofdir = "."
		if fout is None:
			fout = self.getName()
		ofname = ofdir + "/" + fout+'.'+fmt
		w = int(w)
		h = int(h)
		logger.info('Saving as: %s', ofname)
		self.cvs = ROOT.TCanvas('tcvs_%s'%fout, '', w, h)
		if self.legend.legpos == "R":
			self.cvs.SetRightMargin(0.26)
		self.cvs.SetBottomMargin(0.25)

		self.draw()
		self.cvs.SaveAs(ofname)
		#self.cvs.SaveAs(ofname.replace(fmt, "svg"))
		#self.cvs.SaveAs(ofname.replace(fmt, "gif"))

		if log:
			self.log.save(ofdir + "/" + fout + '.pylog')

	def getName(self):
		if self._plot_params._ofname is not None:
			return self._plot_params._ofname
		else:
			return self._plot_params.getName() + ('_'+self._unique_id if self._unique_id is not None else '')

class StackPlot(Plot):

	def __init__(self, plot_params, sample_list, unique_id, **kwargs):
		super(StackPlot, self).__init__(plot_params, sample_list, unique_id, **kwargs)
		self.hist_stack = None
		self.data_hist = None
		self.total_mc_hist = None
		self.mc_hists = None
		self.mc_group_hists = None

	def saveToROOT(self, tfile):
		objects = self.mc_hists + [self.total_mc_hist + self.data_hist]
		super(StackPlot, self).saveToROOT(tfile, objects)

	def draw(self):
		self.hist_stack.Draw('HIST')
		self.hist_stack.SetTitle(self.plotTitle)
		self.hist_stack.GetXaxis().SetTitle(self._plot_params.x_label)
		self.hist_stack.GetYaxis().SetTitle('Events / bin')

		self.data_hist.Draw('E1 SAME')
		self.total_mc_hist.Draw("E2 SAME")
		super(StackPlot, self).draw()

	def setLegendEntries(self, legend):
		if self.mc_group_hists is None:
			raise ValueError("mc_group_hists was not set!")
		for hist in self.mc_group_hists.values() + [self.total_mc_hist]:
			legend.AddEntry(hist, hist.GetTitle(), "F")
		legend.AddEntry(self.data_hist, self.data_hist.GetTitle())
		return

	def getHistogram(self, name):
		if name == "data":
			return self.data_hist
		elif name == "mc":
			return self.total_mc_hist
		elif name in self.mc_group_hists.keys():
			return self.mc_group_hists[name]
		elif name in self.mc_hists.keys():
			return self.mc_hists.keys[name]
		else:
			raise KeyError("Histogram '{0}' not defined for plot {1}".format(name, self))

	def getHistograms(self):
		return [self.data_hist] + self.mc_group_hists.values()

class ShapePlot(Plot):
	def __init__(self, plot_params, sample_list, unique_id):
		super(ShapePlot,self).__init__(plot_params, sample_list, unique_id)
		self._hists = {}
		self._maxbin = None

	def saveToROOT(self, tfile):
		objects = self._hists.values()
		super(ShapePlot, self).saveToROOT(tfile, objects)

	def addHist(self, h, name):
		self._hists[name] = h

	def draw(self):
		first = True
		hists = self._hists.values()

		max_bin = max([h.GetMaximum() for h in self._hists.values()])
		min_bin = min([h.GetMinimum() for h in self._hists.values()])
		hists[0].SetMaximum(1.5*max_bin)
		hists[0].SetMinimum(0.001 if self._plot_params._ymin is None else self._plot_params._ymin)
		hists[0].GetXaxis().SetTitle(self._plot_params.x_label)
		for hist in hists:
			hist.Draw('E1' if first else 'E1 SAME')
			first = False
		super(ShapePlot, self).draw()

		#need to set after drawing all other things, since histo title will change, but is used internally
		hists[0].SetTitle(self.plotTitle)

	def setLegendEntries(self, legend):
		for hist in self._hists.values():
			legName = hist.GetTitle()
			if self._plot_params.stat_opts == "legend":
				legName = "#splitline{%s}{mean=%.2f rms=%.2f}" % (hist.GetTitle(), hist.GetMean(), hist.GetRMS())
			legend.AddEntry(hist, legName)
		return

	def getHistogram(self, name):
		return self._hists[name]

	def getHistograms(self):
		return self._hists.values()

class BaseLegend(object):
	legCoords = dict()
	legCoords["R_full"] = [0.75, 0.01, 0.99, 0.99]
	legCoords["R"] = [0.75, 0.35, 0.99, 0.95]

	def __init__(self, plot, legpos="R"):
		self.legpos = legpos
		coords = BaseLegend.legCoords[self.legpos]

		self.legend = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])
		self.legend.SetFillColor(ROOT.kWhite)
		self.legend.SetLineColor(ROOT.kWhite)
		#self.legend.SetTextFont(230)
		self.legend.SetTextSize(text_size)
		self.legend.SetFillStyle(4000)

		plot.setLegendEntries(self.legend)

	def Draw(self, args=""):
		return self.legend.Draw(args)

class YieldTable:
	pos = dict()
	#pos["RL"] = [0.75, 0.0, 0.99, 0.24]
	pos["RL"] = [0.7585, 0.024, 0.997, 0.2768]

	def __init__(self, samples, plot, location="RL"):
		self.samples = samples
		self.plot = plot

		yield_table = dict()
		for group_name, group in self.samples.groups.items():
			name = group.pretty_name
			hist = plot.getHistogram(group.name)
			total_int = hist.get_integral() if not hist.is_normalized else hist.count_events
			total_err = hist.get_err() if not hist.is_normalized else math.sqrt(hist.count_events)
			yield_table[name] = (total_int, total_err)

		cur_pos = YieldTable.pos[location]
		self.text_pad = ROOT.TPaveText(cur_pos[0], cur_pos[1], cur_pos[2], cur_pos[3], "NDC")
		self.text_pad.SetFillColor(ROOT.kWhite)
		#self.text_pad.SetTextFont(220)
		self.text_pad.SetTextSize(0.8*text_size)
		#self.text_pad.SetLabel("event yields")
		self.text_pad.SetShadowColor(ROOT.kWhite)
		for (name, (total, err)) in yield_table.items():
			self.text_pad.AddText("{0}: {1:.1f} #pm {2:.1f}".format(name, total, err))

	def draw(self):
		self.text_pad.Draw()

class Chi2ValuePad:
	pos = dict()
	pos["LU"] = [0.1, 0.8, 0.2, 0.9]
	pos["RU_inset"] = [0.79, 0.58, 0.69, 0.88]
	pos["RL"] = [0.1, 0.1, 0.2, 0.2]
	def __init__(self, hist_a, hist_b, location="RL", chi2options=None):

		chi2opt = "CHI2/NDF"
		if chi2options is None:
			chi2options = dict()
			chi2options["weight_type"] = "WW"
			#chi2options["descr"] = "({hist_a_title}, {hist_b_title})"
		chi2opt += chi2options["weight_type"]

		self.chi2 = hist_a.Chi2Test(hist_b, chi2opt)
		cur_pos = Chi2ValuePad.pos[location]
		self.text_pad = ROOT.TPaveText(cur_pos[0], cur_pos[1], cur_pos[2], cur_pos[3], "NDC")
		self.text_pad.SetFillColor(ROOT.kWhite)
		self.text_pad.SetLineColor(ROOT.kWhite)
		self.text_pad.SetFillStyle(4000)
		self.text_pad.SetShadowColor(ROOT.kWhite)
		#self.text_pad.SetTextFont(220)
		self.text_pad.SetTextSize(text_size)
		self.text_pad.AddText("#chi^{2}/NDF = %.1f" % (self.chi2))

	def draw(self):
		self.text_pad.Draw()
