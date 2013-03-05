import ROOT
import logging, time
from zlib import adler32
import random
import string
import methods,params,plotlog
from methods import Sample, MCSample, DataSample, SampleGroup, SampleList
from methods import PlotParams, SampleListGenerator
import cPickle as pickle
import multiprocessing
import pdb
import math
from odict import OrderedDict as dict

text_size = 0.025

logger = logging.getLogger(__name__)
def mp_applyCut(s):
	return PlotCreator._applyCut(s[0], s[1], s[2], s[3], s[4])


class PlotCreator(object):
	def __init__(self, frac = 1.0, n_cores=10):
		self.frac_entries = frac
		self.samples = None
		self.set_n_cores(n_cores)

	@staticmethod
	def _uniqueCutStr(cut_str, weight_str):
		"""
		Returns a unique hash for the plot_params.weight*cut_str object
		"""
		uniq = adler32("({0})*({1})".format(weight_str, cut_str))
		return uniq

	def set_n_cores(self, n_cores):
		self.n_cores = n_cores
		self.run_multicore = self.n_cores > 1
		if self.run_multicore:
			logger.info("Switching to multicore mode: n_cores=%d" % self.n_cores)
		else:
			logger.info("Switching to single core mode")

	def _switchBranchesOn(self, vars_to_switch):
		sample_list = self.getSamples()
		logger.debug("Switching branches ON: {0} for samples {1}".format(vars_to_switch, sample_list))

		for sample in sample_list:
			sample.tree.SetBranchStatus("*", 0)

		for var in vars_to_switch:
			for sample in sample_list:
				sample.tree.SetBranchStatus(var, 1)

		return


	@staticmethod
	def _applyCut(cutstr, s, reset=True, frac_entries=1, multicore=True):
		"""
		Apply the cut 'cutstr' on sample 's'. Optionally reset the tree event list
		before cutting and process only a limited number of entries.
		"""
		t_cut = time.time()
		logger.debug('Cutting on `%s`', s.name)

		if multicore:
			tempSample = Sample.fromOther(s)
		else:
			tempSample = s
		tempSample.tfile.cd()

		if reset:
			tempSample.tree.SetEventList(0)

		logger.debug("Drawing event list for sample {0}".format(tempSample.name))
		uniqueName = tempSample.name + '_' + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))

		elist_name = "elist_"+uniqueName
		nEvents = tempSample.tree.Draw(">>%s"%elist_name, cutstr, '', int(float(tempSample.tree.GetEntries())*frac_entries))
		logger.debug("Done drawing {0} events into list {1}".format(nEvents, elist_name))
		elist = tempSample.tfile.Get(elist_name)
		#tempSample.tree.SetEventList(elist)

		retList = pickle.dumps(elist)
		logger.debug('Cutting on `%s` took %f', tempSample.name, time.time() - t_cut)

		del tempSample
		return retList

	def _applyCuts(self, cutstr, smpls, reset=True):
		t_cut = time.time()

		#Combine the parameters into a single list [(cutstr, sample, do_reset, frac_entries), ... ]
		smplArgs = zip([cutstr]*len(smpls),
			smpls,
			[reset]*len(smpls),
			[self.frac_entries]*len(smpls),
			[self.run_multicore]*len(smpls)
		)

		#Apply the cut on samples with multicore
		if self.n_cores>1:
			logger.debug("Cutting using on %d cores" % self.n_cores)
			p = multiprocessing.Pool(self.n_cores)
			evLists = p.map(mp_applyCut, smplArgs)
		else:
			evLists = map(mp_applyCut, smplArgs)

		logger.debug("Done cutting event lists for cut {0} on samples {1}".format(cutstr, smpls))
		#Load the event lists via pickle and set the trees
		for i in range(len(smpls)):
			smpls[i].tree.SetEventList(pickle.loads(evLists[i]))
		logger.debug("Done unpickling and setting event lists")
		logger.info('Cutting on all took %f', time.time()-t_cut)

	def plot(self, cut, plots, cutDescription=""):
		"""Method takes a cut and list of plots and then returns a list plot objects."""

		t0 = time.time()
		# Apply cuts
		self._cutstr = cut.cutStr
		logger.info("Plotting samples {0} with Cut({1}), plots: {2}".format(self.samples, cut, plots))
		logger.debug('Cut string: %s', self._cutstr)

		smpls = self.samples.getSamples()

		self._switchBranchesOn(cut._vars)

		self._applyCuts(self._cutstr, smpls)

		retplots = [self._plot(x) for x in plots]

		for p in retplots:
			p.setPlotTitle(cutDescription)

		t1 = time.time()
		logger.info("Plotting took {0:.1f} seconds".format(t1-t0))


		return retplots


class StackedPlotCreator(PlotCreator):
	"""Class that is used to create stacked plots

	Initalizer takes the data and MC samples which are then plotted.
	datasamples is either of type DataSample, [DataSample] or SampleGroup.
	mcsamples has to be of type SampleList

	"""
	def __init__(self, datasamples, mcsamples):
		super(StackedPlotCreator, self).__init__()
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

#	def plot(self, cut, plots, cutDescription=""):
#		"""Method takes a cut and list of plots and then returns a list plot objects."""
#		# Apply cuts
#		self._cutstr = cut.cutStr
#
#		logger.info('Cut string: %s', self._cutstr)
#
#
#		smpls = self._mcs.getSamples() + self._data.getSamples()
#		self._applyCuts(self._cutstr, smpls)
#
#		# Plot
#		retplots = [self._plot(x) for x in plots]
#
#		for p in retplots:
#			p.setPlotTitle(cutDescription)
#		return retplots

	def getSamples(self):
		return self._mcs.getSamples() + self._data.getSamples()

	def _plot(self, pp):
		"""Internally used plotting method.

		It takes a PlotParams class and returns the corresponding Plot
		object.

		"""
		unique_id = PlotCreator._uniqueCutStr(self._cutstr, pp.getWeightStr())

		self._switchBranchesOn(pp.getVars())

		plotname = 'plot_cut%s_%s' % (unique_id, pp.getName())
		logger.info('Plotting: %s', plotname)

		plot = StackPlot(pp, self.samples, unique_id)
		plot.log.addParam('Variable', pp.var)
		plot.log.addParam('HT min', pp.hmin)
		plot.log.addParam('HT max', pp.hmax)
		plot.log.addParam('HT bins', pp.hbins)

		cut_string = ''
		plot.log.setCuts([''], cut_string)

		# Create log variables
		plot.log.addVariable('filled', 'Events filled')
		plot.log.addVariable('int', 'Integrated events')

		# Create data histogram
		total_luminosity = 0.0
		data_hist_name = '%s_hist_data'%plotname

		plot.data_hist = ROOT.TH1F(data_hist_name, '', pp.hbins, pp.hmin, pp.hmax)
		plot.data_hist.SetMarkerStyle(20)
		plot.data_hist.Sumw2()

		#plot.log.addProcess(dname, ismc=False)
		for d in self._data.getSamples():
			data_hist = ROOT.TH1F(data_hist_name + d.name, '', pp.hbins, pp.hmin, pp.hmax)
			data_hist.Sumw2()

			#for data there is no weight necessary
			dt_filled = d.tree.Draw('%s>>%s'%(pp.var, data_hist.GetName()), '', 'goff')
			total_luminosity += d.luminosity
			dname = d.name
			plot.log.addProcess(dname, ismc=False)
			plot.log.setVariable(dname, 'crsec', d.luminosity)
			plot.log.setVariable(dname, 'fname', d.fname)
			plot.log.setVariable(dname, 'filled', dt_filled)

			err = ROOT.Double()
			dt_int = data_hist.IntegralAndError(1, data_hist.GetNbinsX(), err)

			plot.log.setVariable(dname, 'int', dt_int)
			plot.log.setVariable(dname, 'int_err', float(err))

			plot.data_hist.Add(data_hist)

		#dt_int = plot.data_hist.Integral()

		effective_lumi = total_luminosity
		plot.log.addParam('Luminosity', total_luminosity)
		plot.log.addParam('Effective luminosity', effective_lumi)

		data_max = plot.data_hist.GetMaximum()
		plot.log.addParam('Data binmax', data_max)
		plot.data_hist.SetTitle("L_{int.} = %.1f fb^{-1}" % (plot.log.getParam("Luminosity")/1000.0))
	#	class TempMCS:
	#		def __init__(self, g, s):
	#			self.fname = s.fname
	#			self.name = str(s.name)
	#			self.crsec = s.xs
	#			self.color = g.color
	#			self.tree = s.tree
	#			self.group = g
	#			self.sample = s
	#			self._totev = s.getTotalEvents()
	#		def getTotalEvents(self):
	#			return self._totev

	#	temp_mcs = []
	#	for gk in self._mcs.groups:
	#		g = self._mcs.groups[gk]
	#		for s in g.samples:
	#			temp_mcs.append(TempMCS(g, s))

		mc_int = 0
		plot.mc_hists = []
		plot.mc_group_hists = dict()


		for group_name, group in self._mcs.groups.items():
			group_hist_name = 'hist_%s_mc_group_%s'%(plotname, group_name)
			mc_group_hist = ROOT.TH1F(group_hist_name, group.pretty_name, pp.hbins, pp.hmin, pp.hmax)
			mc_group_hist.filled_count = 0
			mc_group_hist.Sumw2()
			mc_group_hist.SetFillColor(group.color)
			mc_group_hist.SetLineColor(group.color)
			mc_group_hist.SetLineWidth(0)
			for sample in group.samples:
				plot.log.addProcess(sample.name)
				plot.log.setVariable(sample.name, 'crsec', sample.xs)
				plot.log.setVariable(sample.name, 'fname', sample.fname)
				hist_name = group_hist_name + "_" + sample.name

				mc_hist = ROOT.TH1F(hist_name, group.pretty_name, pp.hbins, pp.hmin, pp.hmax)
				mc_hist.Sumw2()
				#mc_hist.SetFillColor(group.color)
				#mc_hist.SetLineColor(group.color)
				#mc_hist.SetLineWidth(0)

				mc_filled = sample.tree.Draw('%s>>%s'%(pp.var, hist_name), pp.getWeightStr(sample.disabled_weights), 'goff')
				mc_hist.filled_count = mc_filled
				plot.log.setVariable(sample.name, 'filled', mc_filled)

				# MC scaling to xs
				expected_events = sample.xs * effective_lumi
				total_events = sample.getTotalEvents()
				scale_factor = float(expected_events)/float(total_events)
				mc_hist.Scale(scale_factor)

				plot.mc_hists.append(mc_hist)
				mc_group_hist.Add(mc_hist)
				mc_group_hist.filled_count += mc_hist.filled_count

				err = ROOT.Double()
				mc_int = mc_hist.IntegralAndError(1, mc_hist.GetNbinsX(), err)
				plot.log.setVariable(sample.name, 'totev', total_events)
				plot.log.setVariable(sample.name, 'expev', expected_events)
				plot.log.setVariable(sample.name, 'scf', scale_factor)
				plot.log.setVariable(sample.name, 'int', mc_int)
				plot.log.setVariable(sample.name, 'int_err', float(err))
			plot.mc_group_hists[group_name] = mc_group_hist

		# Kolmorogov test
		total_mc_hist = ROOT.TH1F('hist_mc_ktbase_%s'%plotname, 'MC stat. err.', pp.hbins, pp.hmin, pp.hmax)
		total_mc_hist.SetFillStyle(3004) #show only error band
		total_mc_hist.SetFillColor(ROOT.kBlue+3)
		total_mc_hist.SetLineColor(ROOT.kBlue+3)

		sorted_group_hists = dict()
		for name, val in sorted(plot.mc_group_hists.items(), key=lambda x: x[1].filled_count):
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
		plot_title = '%s (%s)'%(pp.var, plotname)
		plot.hist_stack = ROOT.THStack('stack_%s'%plotname, plot_title)

		for hist in reversed(plot.mc_group_hists.values()):
			plot.hist_stack.Add(hist)

		plot.legend = BaseLegend(self._mcs.groups, plot)

		plot.hist_stack.SetMaximum(1.1*max(data_max, mc_max))

		# return the plot object where it can be drawn etc.
		return plot

class ShapePlotCreator(PlotCreator):
	"""Create plots for sample shape comparison."""
	def __init__(self, samples):
		super(ShapePlotCreator, self).__init__()
		self._slist = samples
		self.samples = self._slist

	def getSamples(self):
		return self._slist.getSamples()

	def _plot(self, plot_params):

		uniq = PlotCreator._uniqueCutStr(self._cutstr, plot_params.getWeightStr())

		plot = ShapePlot(plot_params, self.samples, unique_id=uniq)
		plotname = 'plot_cut%s_%s' % (uniq, plot_params.getName())
		logger.debug('Plotting: %s', plotname)

		self._switchBranchesOn(plot_params.getVars())

		# Create the histograms
		plot._maxbin = 0.0
		for group_name, group in self._slist.groups.items():
			hist_name = 'hist_%s_%s'%(plotname, group.getName())
			logger.info('Created histogram: %s', hist_name)

			hist = ROOT.TH1F(hist_name, group.pretty_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
			hist.Sumw2()
			hist.SetStats(False)
			hist.SetLineColor(group.color)
			hist.SetLineWidth(3)

			filled_tot = 0.0
			for s in group.getSamples():
				sample_hist = ROOT.TH1F(hist_name + s.name, group.pretty_name, plot_params.hbins, plot_params.hmin, plot_params.hmax)
				sample_hist.Sumw2()

				plot.log.addProcess(s.name)
				filled = s.tree.Draw(
						'%s>>%s'%(plot_params.var, sample_hist.GetName()),
					plot_params.getWeightStr(s.disabled_weights) if isinstance(s, MCSample) else '', 'goff'
				)
				logger.debug('Filled histogram `%s` from sample `%s` with %f events', hist_name, s.name, filled)
				filled_tot += filled

				err = ROOT.Double()
				integral = sample_hist.IntegralAndError(1, sample_hist.GetNbinsX(), err)
				plot.log.setVariable(s.name, 'int', integral)
				plot.log.setVariable(s.name, 'int_err', float(err))

				hist.Add(sample_hist)

			logger.debug('Filled total for `%s` : %f' % (hist_name, filled_tot))

			hist_integral = hist.Integral()
			logger.debug('Hist `%s` integral: %f' % (hist_name, hist_integral))
			if filled_tot>0:
				hist.Scale(1.0/hist_integral)
				logger.debug('Hist `%s` integral: %f (after scaling)' % (hist_name, hist.Integral()))
			else:
				logger.warning("Histogram {0} was empty".format(hist))
				hist.Scale(0)
			plot._maxbin = max(plot._maxbin, hist.GetMaximum())
			plot.addHist(hist, group.name)

		plot.legend = BaseLegend(self._slist.groups, plot)

		return plot

class Plot(object):
	"""This class represents a single plot and has the methods to export it.

	This class puts everything together (different histograms, legend etc)
	and allows to export the plot easily. It also handles the metadata
	logger.

	"""
	def __init__(self, plot_params, groups, unique_id):
		self.log = plotlog.PlotLog()
		self._plot_params = plot_params
		self._unique_id = str(unique_id)
		self.groups = groups


	def setPlotTitle(self, cutDescription=""):
		self.cutDescription = cutDescription
		self.plotTitle = self._plot_params.plotTitle + " in " + self.cutDescription


	def draw(self):
		self.yield_table = YieldTable(self.groups, self)
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

	def save(self, w=650, h=400, log=False, fmt='png', fout=None):
		if fout is None:
			fout = self.getName()
		ofname = fout+'.'+fmt

		logger.info('Saving as: %s', ofname)
		self.cvs = ROOT.TCanvas('tcvs_%s'%fout, '', w, h)
		if self.legend.legpos == "R":
			self.cvs.SetRightMargin(0.26)
		self.cvs.SetBottomMargin(0.25)

		self.draw()
		self.cvs.SaveAs(ofname)
		self.cvs.SaveAs(ofname.replace(fmt, "svg"))
		#self.cvs.SaveAs(ofname.replace(fmt, "gif"))

		if log:
			self.log.save(fout+'.pylog')

	def getName(self):
		if self._plot_params._ofname is not None:
			return self._plot_params._ofname
		else:
			return self._plot_params.getName() + ('_'+self._unique_id if self._unique_id is not None else '')

class StackPlot(Plot):

	def __init__(self, plot_params, groups, unique_id):
		super(StackPlot, self).__init__(plot_params, groups, unique_id)
		self.hist_stack = None
		self.data_hist = None
		self.total_mc_hist = None
		self.mc_hists = None
		self.mc_group_hists = None

	def draw(self):
		self.hist_stack.Draw('HIST')
		self.hist_stack.SetTitle(self.plotTitle)
		self.hist_stack.GetXaxis().SetTitle(self._plot_params.x_label)
		self.hist_stack.GetYaxis().SetTitle('Events / bin')

		self.data_hist.Draw('E1 SAME')
		self.total_mc_hist.Draw("E4 SAME")
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
		elif name in mc_group_hists.keys():
			return self.mc_group_hists[name]
		elif name in mc_hists.keys():
			return self.mc_hists.keys[name]
		else:
			raise KeyError("Histogram '{0}' not defined for plot {1}".format(name, self))

class ShapePlot(Plot):
	def __init__(self, plot_params, groups, unique_id):
		super(ShapePlot,self).__init__(plot_params, groups, unique_id)
		self._hists = {}
		self._maxbin = None

	def addHist(self, h, name):
		self._hists[name] = h

	def draw(self):
		first = True
		hists = self._hists.values()
		hists[0].SetMaximum(1.1*self._maxbin)
		for hist in hists:
			hist.Draw('E1' if first else 'E1 SAME')
			first = False
		super(ShapePlot, self).draw()

		#need to set after drawing all other things, since histo title will change, but is used internally
		hists[0].SetTitle(self.plotTitle)

	def setLegendEntries(self, legend):
		for hist in self._hists.values():
			legend.AddEntry(hist, hist.GetTitle())
		return

	def getHistogram(self, name):
		return self._hists[name]

class BaseLegend(object):
	legCoords = dict()
	legCoords["R_full"] = [0.75, 0.01, 0.99, 0.99]
	legCoords["R"] = [0.75, 0.35, 0.99, 0.95]

	def __init__(self, groups, plot, legpos="R"):
		self.legpos = legpos
		coords = BaseLegend.legCoords[self.legpos]

		self.legend = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])
		self.legend.SetFillColor(ROOT.kWhite)
		self.legend.SetLineColor(ROOT.kWhite)
		#self.legend.SetTextFont(230)
		self.legend.SetTextSize(text_size)
		self.legend.SetFillStyle(4000)

		plot.setLegendEntries(self.legend)

		# Old code for reversing:
		#for name, group in reversed(groups.items()):
		#	firstHistoName = groups[name].samples[0].name
		#	self.legend.AddEntry(plot.mc_histMap[firstHistoName], group.prettyName, "F")
		#self.legend.AddEntry(plot.dt_hist, "L_{int.} = %.1f fb^{-1}" % (plot.log.getParam("Luminosity")/1000.0))

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
			total_int = sum([plot.log._processes[x.name]["vars"]["int"] for x in group.samples])
			total_err = math.sqrt(sum(map(lambda x: x**2, [plot.log._processes[x.name]["vars"]["int_err"] for x in group.samples])))
			yield_table[group_name] = (total_int, total_err)

		cur_pos = YieldTable.pos[location]
		self.text_pad = ROOT.TPaveText(cur_pos[0], cur_pos[1], cur_pos[2], cur_pos[3], "NDC")
		self.text_pad.SetFillColor(ROOT.kWhite)
		#self.text_pad.SetTextFont(220)
		self.text_pad.SetTextSize(text_size)
		self.text_pad.SetLabel("event yields")
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
		self.text_pad.AddText("#chi^{2}/NDF(%s, %s) = %.1f" % (hist_a.GetTitle(), hist_b.GetTitle(), self.chi2))

	def draw(self):
		self.text_pad.Draw()

#class GroupLegend(BaseLegend):
#
#	def __init__(self, groups, plot, legpos="R"):
#		super(GroupLegend, self).__init__(groups, plot, legpos)
#		for name, group in groups.items():
#			firstHistoName = groups[name].samples[0].name
#			legName = group.pretty_name
#			self.legend.AddEntry(plot.mc_histMap[firstHistoName], legName, "F")
#		if hasattr(plot, "data_hist"):
#			self.legend.AddEntry(plot.data_hist, "L_{int.} = %.1f fb^{-1}" % (plot.log.getParam("Luminosity")/1000.0))
#
#	@staticmethod
#	def sampleLegendName(group, plot):
#		name = group.pretty_name
#		total_int = sum([plot.log._processes[x.name]["vars"]["int"] for x in group.samples])
#		total_err = math.sqrt(sum(map(lambda x: x**2, [plot.log._processes[x.name]["vars"]["int_err"] for x in group.samples])))
#		return "#splitline{%s}{%s}" % (name, "N_{{exp}} = {0:.1f} #pm {1:.1f}".format(total_int, total_err))

#class ShapeGroupLegend(GroupLegend):
#	def __init__(self, groups, plot, legpos="R"):
#		super(BaseLegend, self).__init__(groups, plot, legpos)
#		for name,hist in plot._hists.items():
#			self.legend.AddEntry(hist, name, "F")
