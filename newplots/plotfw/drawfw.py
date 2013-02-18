import ROOT
import logging
import methods,params,plotlog
from methods import Sample, MCSample, DataSample, SampleList, PlotParams

def addAutoSample(samplelist, groupname, samplename, fname):
	"""Helper function that adds a MC sample to a SampleList.
	
	It uses the color and cross sections defined in params.py to do that.
	
	"""
	if groupname not in samplelist.groups:
		g = methods.SampleGroup(groupname, params.colors[samplename])
		samplelist.addGroup(g)
		
	# Create the sample
	if samplename in params.xs:
		xs = params.xs[samplename]
	else:
		logging.warning('Notice: cross section fallback to group (g: %s, s: %s)', groupname, samplename)
		xs = params.xs[groupname] 
	s = methods.MCSample(fname, xs, samplename, directory=samplelist.directory)
	samplelist.groups[groupname].add(s)

class StackedPlotCreator:
	"""Class that is used to create stacked plots (based on samples)"""
	def __init__(self, datasample, mcsamples):
		self._mcs = mcsamples
		self._data = datasample
	
	def plot(self, cut, plots):
		"""Method takes a cut and list of plots and then returns a list plot objects."""
		# Apply cuts
		self._cutstr = cut.cutStr
		
		# Plot
		retplots = []
		for p in plots:
			mpo = self._plot(p)
			#mpo.save(p.var, log=False)
			retplots.append(mpo)
		return retplots
	
	def _plot(self, pp):
		"""Internally used plotting method.
		
		It takes a PlotParams class and returns the corresponding Plot
		object.
		
		"""
		print 'Plotting:', pp
		
		plotname = 'plot_' + pp.getName()
		
		p = Plot(pp)
		p.log.addParam('Variable', pp.var)
		p.log.addParam('HT min', pp.hmin)
		p.log.addParam('HT max', pp.hmax)
		p.log.addParam('HT bins', pp.hbins)
		#p.log.addParam('Integrated scaling', str(intsc))
		
		cut_string = self._cutstr
		p.log.setCuts([''], cut_string)
		
		# Create the legend
		p.legend = ROOT.TLegend(0.80, 0.65, 1.00, 0.90)
		
		# Create log variables
		p.log.addVariable('filled', 'Events filled')
		p.log.addVariable('int', 'Integrated events')
		
		# Create histograms
		p.log.addProcess('data', ismc=False)
		p.log.setVariable('data', 'crsec', self._data.luminosity)
		p.log.setVariable('data', 'fname', self._data.fname)
		p.dt_hist = ROOT.TH1F('%s_hist_data'%plotname, '', pp.hbins, pp.hmin, pp.hmax)
		p.dt_hist.SetMarkerStyle(20)
		p.log.setVariable('data', 'filled', self._data.tree.Draw('%s>>hist_data'%pp.var, cut_string, 'goff'))
		dt_int = p.dt_hist.Integral()
		p.log.setVariable('data', 'int', dt_int)
		
		#effective_lumi = self._data.luminosity*float(self._data.tree.GetEntries())/float(self._data.getTotalEvents())
		# TODO: implement effectice luminosity
		effective_lumi = self._data.luminosity
		p.log.addParam('Luminosity', self._data.luminosity)
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
		for mc in temp_mcs:
			p.log.addProcess(mc.name)
			p.log.setVariable(mc.name, 'crsec', mc.crsec)
			p.log.setVariable(mc.name, 'fname', mc.fname)
			hist_name = 'hist_%s_mc_%s'%(plotname, mc.name)
			
			mc_hist = ROOT.TH1F(hist_name, '', pp.hbins, pp.hmin, pp.hmax)
			mc_hist.SetFillColor(mc.color)
			mc_hist.SetLineWidth(0)
			p.mc_hists.append(mc_hist)
			
			p.log.setVariable(mc.name, 'filled', mc.tree.Draw('%s>>%s'%(pp.var,hist_name), cut_string, 'goff'))
			
			# MC scaling
			expected_events = mc.crsec*effective_lumi
			total_events = mc.getTotalEvents()
			scale_factor = float(expected_events)/float(total_events)
			mc_hist.Scale(scale_factor)
			
			p.legend.AddEntry(mc_hist, mc.name, 'F')
			
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
	def __init__(self, pp):
		self.log = plotlog.PlotLog()
		self._pp = pp
	
	def draw(self):
		self.stack.Draw('')
		self.dt_hist.Draw('E1 SAME')
		self.legend.Draw('SAME')
	
	def save(self, w=550, h=400, log=False, fmt='png', fout=None):
		if fout is None:
			fout = self._pp.getName()
		ofname = fout+'.'+fmt
		
		logging.info('Saving as: %s', ofname)
		self.cvs = ROOT.TCanvas('tcvs_%s'%self._pp.var, self._pp.var, w, h)
		self.draw()
		self.cvs.SaveAs(ofname)
		
		if log:
			self.log.save(fout+'.pylog')
