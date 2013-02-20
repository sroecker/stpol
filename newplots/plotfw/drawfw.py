import ROOT
import logging, time
from zlib import adler32
import random
import string
import methods,params,plotlog
from methods import Sample, MCSample, DataSample, SampleGroup, SampleList
from methods import PlotParams

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
			g = methods.SampleGroup(groupname, params.colors[samplename])
			self._samplelist.addGroup(g)

		# Create the sample
		if samplename in params.xs:
			xs = params.xs[samplename]
		else:
			logging.warning('Notice: cross section fallback to group (g: %s, s: %s)', groupname, samplename)
			xs = params.xs[groupname]
		s = methods.MCSample(fname, xs, samplename, directory=self._directory)
		self._samplelist.groups[groupname].add(s)

	def getSampleList(self):
		return self._samplelist

class PlotCreator(object):
	def __init__(self):
		pass
	
	def _applyCut(self, cutstr, s, reset=True):
		ROOT.gROOT.cd()
		
		t_cut = time.clock()
		logging.info('Cutting on `%s`', s.name)
		t_cut = time.clock()

		if reset:
			s.tree.SetEventList(0) # reset TTree
			#s.tree.SetEntryList(0)

		logging.debug("Drawing event list for sample {0} with cut {1}".format(s.name, cutstr))
		uniqueName = s.name + "_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
		elist_name = "elist_"+uniqueName
		nEvents = s.tree.Draw(">>%s"%elist_name, cutstr)
		logging.debug("Done drawing {0} events into list {1}".format(nEvents, elist_name))
		elist = ROOT.gROOT.Get(elist_name)
		s.tree.SetEventList(elist)

		logging.debug('Cutting on `%s` took %f', s.name, time.clock()-t_cut)
	
	def _applyCuts(self, cutstr, smpls, reset=True):
		t_cut = time.clock()
		map(lambda s: self._applyCut(cutstr, s, reset=reset), smpls)
		logging.debug('Cutting on all took %f', time.clock()-t_cut)
		

class StackedPlotCreator(PlotCreator):
	"""Class that is used to create stacked plots

	Initalizer takes the data and MC samples which are then plotted.
	datasamples is either of type DataSample, [DataSample] or SampleGroup.
	mcsamples has to be of type SampleList

	"""
	def __init__(self, datasamples, mcsamples):
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
		retplots = map(self._plot, plots)
		for p in retplots:
			p.setPlotTitle(cutDescription)
		return retplots

	def _plot(self, pp):
		"""Internally used plotting method.

		It takes a PlotParams class and returns the corresponding Plot
		object.

		"""
		print 'Plotting:', pp

		plotname = 'plot_cut%s_%s' % (adler32(self._cutstr), pp.getName())
		logging.info('Plotting: %s', plotname)

		p = Plot(pp, cutstring=adler32(self._cutstr))
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
		for d in self._data.getSamples():
			dt_filled = d.tree.Draw('%s>>+%s'%(pp.var, dt_hist_name), cut_string, 'goff')
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
			mc_hist.SetFillColor(mc.color)
			mc_hist.SetLineColor(mc.color)
			mc_hist.SetLineWidth(0)
			p.mc_hists.append(mc_hist)

			p.mc_histMap[mc.name] = mc_hist

			mc_filled = mc.tree.Draw('%s>>%s'%(pp.var,hist_name), cut_string, 'goff')
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
		basemc = ROOT.TH1F('hist_mc_ktbase', '', pp.hbins, pp.hmin, pp.hmax)
		for mc_hist in p.mc_hists:
			basemc.Add(mc_hist)

		mc_max = basemc.GetMaximum()
		p.log.addParam('MC binmax', mc_max)

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

class Plot:
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
		self.legend.Draw('SAME')

	def save(self, w=550, h=400, log=False, fmt='png', fout=None):
		if fout is None:
			fout = self._pp.getName() + ('_'+self._cutstring if self._cutstring is not None else '')
		ofname = fout+'.'+fmt

		logging.info('Saving as: %s', ofname)
		self.cvs = ROOT.TCanvas('tcvs_%s'%fout, self.plotTitle, w, h)
		if self.legend.legpos == "R":
			self.cvs.SetRightMargin(0.36)

		self.draw()
		self.cvs.SetLogy(self._pp.doLogY)
		self.stack.SetTitle(self.plotTitle)
		self.cvs.SaveAs(ofname)

		if log:
			self.log.save(fout+'.pylog')

class GroupLegend:
	legCoords = dict()
	legCoords["R"] = [0.65, 0.12, 0.99, 0.90]

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
