import ROOT
import logging, time
from zlib import adler32
import random
import string
import methods,params,plotlog
from methods import Sample, MCSample, DataSample, SampleGroup, SampleList
from methods import PlotParams
import pickle
import multiprocessing
import marshal

def mp_applyCut(s):
	return PlotCreator._applyCut(s[0], s[1], s[2], s[3])


class PlotCreator(object):
	def __init__(self):
		self.frac_entries = 0.2
		pass

	@staticmethod
	def _uniqueCutStr(cut_str, weight_str):
		"""
		Returns a unique hash for the plot_params.weight*cut_str object
		"""
		uniq = adler32("({0})*({1})".format(weight_str, cut_str))
		return uniq

	def _switchBranchesOn(self, var_list):
		sample_list = self.getSamples()
		logging.debug("Switching branches ON: {0} for samples {1}".format(var_list, sample_list))

		for sample in sample_list:
			sample.tree.SetBranchStatus("*", 0)

		for var in var_list:
			for sample in sample_list:
				sample.tree.SetBranchStatus(var, 1)

		return


	@staticmethod
	def _applyCut(cutstr, s, reset=True, frac_entries=1):
		t_cut = time.clock()
		logging.info('Cutting on `%s`', s.name)

		tempSample = Sample.fromOther(s)
		tempSample.tfile.cd()

		if reset:
			tempSample.tree.SetEventList(0) # reset TTree
			#s.tree.SetEntryList(0)

		logging.debug("Drawing event list for sample {0} with cut {1}".format(tempSample.name, cutstr))
		uniqueName = tempSample.name + "_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
		elist_name = "elist_"+uniqueName
		nEvents = tempSample.tree.Draw(">>%s"%elist_name, cutstr, '', int(float(tempSample.tree.GetEntries())*frac_entries))
		logging.debug("Done drawing {0} events into list {1}".format(nEvents, elist_name))
		elist = tempSample.tfile.Get(elist_name)
		#tempSample.tree.SetEventList(elist)

		retList = pickle.dumps(elist)
		logging.debug('Cutting on `%s` took %f', tempSample.name, time.clock() - t_cut)

		del tempSample
		return retList

	def _applyCuts(self, cutstr, smpls, reset=True):
		t_cut = time.clock()
		#p = multiprocessing.Pool(24)

		#Combine the parameters into a single list [(cutstr, sample, do_reset, frac_entries), ... ]
		smplArgs = zip([cutstr]*len(smpls), smpls, [reset]*len(smpls), [self.frac_entries]*len(smpls))

		#Apply the cut on samples with multicore
		#evLists = p.map(mp_applyCut, smplArgs)
		evLists = map(mp_applyCut, smplArgs)

		logging.debug("Done cutting event lists for cut {0} on samples {1}".format(cutstr, smpls))
		#Load the event lists via pickle and set the trees
		for i in range(len(smpls)):
			smpls[i].tree.SetEventList(pickle.loads(evLists[i]))
		logging.debug("Done unpickling and setting event lists")
		logging.info('Cutting on all took %f', time.clock()-t_cut)


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
			logging.error('Bad type for `datasamples`!')


	def plot(self, cut, plots, cutDescription=""):
		"""Method takes a cut and list of plots and then returns a list plot objects."""
		# Apply cuts
		self._cutstr = cut.cutStr

		logging.info('Cut string: %s', self._cutstr)


		smpls = self._mcs.getSamples() + self._data.getSamples()
		self._applyCuts(self._cutstr, smpls)

		# Plot
		retplots = [self._plot(x) for x in plots]

		for p in retplots:
			p.setPlotTitle(cutDescription)
		return retplots

	def getSamples(self):
		return self._mcs.getSamples() + self._data.getSamples()

	def _plot(self, pp):
		"""Internally used plotting method.

		It takes a PlotParams class and returns the corresponding Plot
		object.

		"""
		print 'Plotting:', pp
		uniq = PlotCreator._uniqueCutStr(self._cutstr, pp.getWeightStr())

		plotname = 'plot_cut%s_%s' % (uniq, pp.getName())
		logging.info('Plotting: %s', plotname)

		p = Plot(pp, cutstring=uniq)
		p.log.addParam('Variable', pp.var)
		p.log.addParam('HT min', pp.hmin)
		p.log.addParam('HT max', pp.hmax)
		p.log.addParam('HT bins', pp.hbins)
		enabledBranches = []
		#p.log.addParam('Integrated scaling', str(intsc))

		#cut_string = self._cutstr
		cut_string = ''
		p.log.setCuts([''], cut_string)

		# Create the legend
		#p.legend = ROOT.TLegend(0.80, 0.65, 1.00, 0.90)

		# Create log variables
		p.log.addVariable('filled', 'Events filled')
		p.log.addVariable('int', 'Integrated events')

		# Create data histogram
		total_luminosity = 0.0
		dt_hist_name = '%s_hist_data'%plotname
		p.dt_hist = ROOT.TH1F(dt_hist_name, '', pp.hbins, pp.hmin, pp.hmax)
		p.dt_hist.SetMarkerStyle(20)
		p.dt_hist.Sumw2()
		for d in self._data.getSamples():

			#for data there is no weight necessary
			dt_filled = d.tree.Draw('%s>>+%s'%(pp.var, dt_hist_name), '', 'goff')
			total_luminosity += d.luminosity
			dname = d.name
			p.log.addProcess(dname, ismc=False)
			p.log.setVariable(dname, 'crsec', d.luminosity)
			p.log.setVariable(dname, 'fname', d.fname)
			p.log.setVariable(dname, 'filled', dt_filled)
			#p.log.setVariable(dname, 'int', dt_int)

		dt_int = p.dt_hist.Integral()


		# TODO: implement effectice luminosity
		#effective_lumi = self._data.luminosity*float(self._data.tree.GetEntries())/float(self._data.getTotalEvents())
		effective_lumi = total_luminosity
		p.log.addParam('Luminosity', total_luminosity)
		p.log.addParam('Effective luminosity', effective_lumi)

		data_max = p.dt_hist.GetMaximum()
		p.log.addParam('Data binmax', data_max)

		class TempMCS:
			def __init__(self, g, s):
				self.fname = s.fname
				self.name = str(s.name)
				self.crsec = s.xs
				self.color = g.color
				self.tree = s.tree

				self._totev = s.getTotalEvents()
			def getTotalEvents(self):
				return self._totev

		temp_mcs = []
		for gk in self._mcs.groups:
			g = self._mcs.groups[gk]
			for s in g.samples:
				temp_mcs.append(TempMCS(g, s))

		mc_int = 0
		p.mc_hists = []
		p.mc_histMap = dict()
		for mc in temp_mcs:
			p.log.addProcess(mc.name)
			p.log.setVariable(mc.name, 'crsec', mc.crsec)
			p.log.setVariable(mc.name, 'fname', mc.fname)
			hist_name = 'hist_%s_mc_%s'%(plotname, mc.name)

			mc_hist = ROOT.TH1F(hist_name, '', pp.hbins, pp.hmin, pp.hmax)
			mc_hist.Sumw2()
			mc_hist.SetFillColor(mc.color)
			mc_hist.SetLineColor(mc.color)
			mc_hist.SetLineWidth(0)
			p.mc_hists.append(mc_hist)

			p.mc_histMap[mc.name] = mc_hist

			mc_filled = mc.tree.Draw('%s>>%s'%(pp.var,hist_name), pp.getWeightStr(), 'goff')
			p.log.setVariable(mc.name, 'filled', mc_filled)

			# MC scaling
			expected_events = mc.crsec*effective_lumi
			total_events = mc.getTotalEvents()
			scale_factor = float(expected_events)/float(total_events)
			mc_hist.Scale(scale_factor)

			#p.legend.AddEntry(mc_hist, mc.name, 'F')

			mc_int += mc_hist.Integral()

			p.log.setVariable(mc.name, 'totev', total_events)
			p.log.setVariable(mc.name, 'expev', expected_events)
			p.log.setVariable(mc.name, 'scf', scale_factor)
			p.log.setVariable(mc.name, 'int', mc_int)

		'''
		if intsc:
			for mc_hist in p.mc_hists:
				mc_hist.Scale(dt_int/mc_int)
		'''

		# Kolmorogov test
		basemc = ROOT.TH1F('hist_mc_ktbase_%s'%plotname, '', pp.hbins, pp.hmin, pp.hmax)
		basemc.SetFillStyle(3004)
		basemc.SetFillColor(ROOT.kBlue+3)
		basemc.SetLineColor(ROOT.kBlue+3)

		for mc_hist in p.mc_hists:
			basemc.Add(mc_hist)

		mc_max = basemc.GetMaximum()
		p.log.addParam('MC binmax', mc_max)
		p.total_mc = basemc
		p.log.addParam('Kolmogorov test', p.dt_hist.KolmogorovTest(basemc))

		# Stacking the histograms
		plot_title = '%s (%s)'%(pp.var, plotname)
		#if self.chstring is not None:
		#	plot_title += ' [' + str(self.chstring) + ']'
		p.stack = ROOT.THStack('stack_%s'%plotname, plot_title)

		for ht in p.mc_hists:
			p.stack.Add(ht)

		p.legend = GroupLegend(self._mcs.groups, p)

		p.stack.SetMaximum(1.1*max(data_max, mc_max))
		#p.stack.GetXaxis().SetTitle('This is the x-axis title. (GeV)')
		#p.stack.GetYaxis().SetTitle('This is the Y-axis title. (GeV)')

		# return the plot object where it can be drawn etc.
		return p

class ShapePlotCreator(PlotCreator):
	"""Create plots for sample shape comparison."""
	def __init__(self, samples):
		self._slist = samples

	def getSamples(self):
		return self._slist.getSamples()

	def plot(self, cut, plots):
		"""Method takes a cut and list of plots and then returns a list plot objects."""
		# Apply cuts
		self._cutstr = cut.cutStr
		logging.info('Cut string: %s', self._cutstr)

		smpls = self._slist.getSamples()
		self._applyCuts(self._cutstr, smpls)

		# Plot
		return map(self._plot, plots)

	def _plot(self, pp):

		uniq = PlotCreator._uniqueCutStr(self._cutstr, pp.getWeightStr())

		p = ShapePlot(pp, cutstring=uniq)
		plotname = 'plot_cut%s_%s' % (uniq, pp.getName())
		logging.info('Plotting: %s', plotname)

		vars_to_switch = []
		vars_to_switch += [pp.var]
		if pp.weights is not None:
			vars_to_switch += pp.weights
		self._switchBranchesOn(vars_to_switch)

		# Create the histograms
		for gk in self._slist.groups:
			g = self._slist.groups[gk]
			hist_name = 'hist_%s_%s'%(plotname, g.getName())
			logging.info('Created histogram: %s', hist_name)

			hist = ROOT.TH1F(hist_name, '', pp.hbins, pp.hmin, pp.hmax)
			hist.SetStats(False)
			hist.SetLineColor(g.color)
			#p.mc_histMap[g.name] = hist

			filled_tot = 0.0
			for s in g.getSamples():
				if isinstance(s, MCSample) and pp.weights is not None and set(pp.weights).intersection(set(s.branches)) != set(pp.weights):
					logging.error("Sample {0} does not contain the necessary weights: {1}".format(s, set(pp.weights).difference(set(s.branches))))

				filled = s.tree.Draw('%s>>+%s'%(pp.var, hist_name), pp.getWeightStr() if isinstance(s, MCSample) else '', 'goff')
				logging.info('Filled histogram `%s` from sample `%s` with %f events', hist_name, s.name, filled)
				filled_tot += filled
			logging.info('Filled total for `%s` : %f', hist_name, filled_tot)
			hist.Scale(1/filled_tot)
			p.addHist(hist, g.name)

		#dt_int = p.dt_hist.Integral()
		p.legend = ShapeGroupLegend(self._slist.groups, p)

		return p

class Plot(object):
	"""This class represents a single plot and has the methods to export it.

	This class puts everything together (different histograms, legend etc)
	and allows to export the plot easily. It also handles the metadata
	logging.

	"""
	def __init__(self, pp, cutstring=None):
		self.log = plotlog.PlotLog()
		self._pp = pp
		self._cutstring = str(cutstring)


	def setPlotTitle(self, cutDescription=""):
		self.cutDescription = cutDescription
		self.plotTitle = self._pp.plotTitle + " in " + cutDescription


	def draw(self):
		self.stack.Draw('')
		self.dt_hist.Draw('E1 SAME')
		self.total_mc.Draw("E4 SAME")
		self.legend.Draw('SAME')

		self.cvs.SetLogy(self._pp.doLogY)
		self.stack.SetTitle(self.plotTitle)

	def save(self, w=650, h=400, log=False, fmt='png', fout=None):
		if fout is None:
			fout = self.getName()
		ofname = fout+'.'+fmt

		logging.info('Saving as: %s', ofname)
		self.cvs = ROOT.TCanvas('tcvs_%s'%fout, '', w, h)
		if self.legend.legpos == "R":
			self.cvs.SetRightMargin(0.26)

		self.draw()
		self.cvs.SaveAs(ofname)

		if log:
			self.log.save(fout+'.pylog')

	def getName(self):
		if self._pp._ofname is not None:
			return self._pp._ofname
		else:
			return self._pp.getName() + ('_'+self._cutstring if self._cutstring is not None else '')

class ShapePlot(Plot):
	def __init__(self, pp, cutstring=None):
		super(ShapePlot,self).__init__(pp, cutstring)
		#self._hists = []
		self._hists = {}

	def addHist(self, h, name):
		#self._hists.append(h)
		self._hists[name] = h

	def draw(self):
		first = True
		for hk,h in self._hists.items():
			h.Draw('' if first else 'SAME')
			first = False
		self.cvs.SetLogy(self._pp.doLogY)
		self.legend.Draw('SAME')

class GroupLegend:
	legCoords = dict()
	legCoords["R"] = [0.75, 0.25, 0.99, 0.75]

	def __init__(self, groups, plot, legpos="R"):
		self.legpos = legpos
		coords = GroupLegend.legCoords[self.legpos]

		self.legend = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])
		self.legend.SetFillColor(ROOT.kWhite)
		self.legend.SetLineColor(ROOT.kWhite)
		self.legend.SetTextFont(133)
		self.legend.SetTextSize(25)
		self.legend.SetFillStyle(4000)
		for name, group in groups.items():
			firstHistoName = groups[name].samples[0].name
			self.legend.AddEntry(plot.mc_histMap[firstHistoName], group.prettyName, "F")
		self.legend.AddEntry(plot.dt_hist, "L_{int.} = %.1f fb^{-1}" % (plot.log.getParam("Luminosity")/1000.0))

	def Draw(self, args=""):
		return self.legend.Draw(args)

class ShapeGroupLegend(GroupLegend):
	def __init__(self, groups, plot, legpos="R"):
		self.legpos = legpos
		coords = GroupLegend.legCoords[self.legpos]

		self.legend = ROOT.TLegend(coords[0], coords[1], coords[2], coords[3])

		for name,hist in plot._hists.items():
			self.legend.AddEntry(hist, name, "F")
