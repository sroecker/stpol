import methods,params
from methods import SampleList

def addAutoSample(samplelist, groupname, samplename, fname):
	s = methods.Sample(fname, params.xs[samplename], samplename)
	
	if groupname in samplelist.groups:
		samplelist.groups[groupname].add(s)
	else:
		g = methods.SampleGroup(groupname, params.colors[samplename])
		samplelist.addGroup(g)

class PlotStacked:
	def __init__(self):
		return

class DrawCreator:
	def __init__(self, chstring = None):
		self._mcs = []
		self._cuts = []
		self._data = None
		self.chstring = chstring
	
	def addCut(self, cut):
		self._cuts.append(cut)
	
	def getCuts(self):
		pass
	
	def _getCutString(self):
		return '&&'.join(map(lambda s: '('+str(s)+')', self._cuts))
	
	def addMC(self, fname, crsec, name, color=None):
		try:
			newmc = _MCChannel(fname, crsec, name, color)
			self._mcs.append(newmc)
		except IOError as e:
			print e
	
	def setData(self, fname, luminosity):
		self._data = _DataChannel(fname, luminosity)
	
	def plot(self, var, hmin, hmax, hbins, plotname, intsc=False):
		p = Plot()
		p.log.addParam('Variable', var)
		p.log.addParam('HT min', hmin)
		p.log.addParam('HT max', hmax)
		p.log.addParam('HT bins', hbins)
		p.log.addParam('Integrated scaling', str(intsc))
		
		cut_string = self._getCutString()
		p.log.setCuts(self._cuts, cut_string)
		
		# Create the legend
		p.legend = TLegend(0.80, 0.65, 1.00, 0.90)
		
		# Create log variables
		p.log.addVariable('filled', 'Events filled')
		p.log.addVariable('int', 'Integrated events')
		
		# Create histograms
		p.log.addProcess('data', ismc=False)
		p.log.setVariable('data', 'crsec', self._data.luminosity)
		p.log.setVariable('data', 'fname', self._data.fname)
		p.dt_hist = TH1F('hist_data', '', hbins, hmin, hmax)
		p.dt_hist.SetMarkerStyle(20)
		p.log.setVariable('data', 'filled', self._data.tree.Draw('%s>>hist_data'%var, cut_string, 'goff'))
		dt_int = p.dt_hist.Integral()
		p.log.setVariable('data', 'int', dt_int)
		
		#effective_lumi = self._data.luminosity*float(self._data.tree.GetEntries())/float(self._data.getTotalEvents())
		# TODO: implement effectice luminosity
		effective_lumi = self._data.luminosity
		p.log.addParam('Luminosity', self._data.luminosity)
		p.log.addParam('Effective luminosity', effective_lumi)
		
		data_max = p.dt_hist.GetMaximum()
		p.log.addParam('Data binmax', data_max)
		
		mc_int = 0
		p.mc_hists = []
		for mc in self._mcs:
			p.log.addProcess(mc.name)
			p.log.setVariable(mc.name, 'crsec', mc.crsec)
			p.log.setVariable(mc.name, 'fname', mc.fname)
			hist_name = 'hist_%s_mc_%s'%(plotname, mc.name)
			
			mc_hist = TH1F(hist_name, '', hbins, hmin, hmax)
			mc_hist.SetFillColor(mc.color)
			mc_hist.SetLineWidth(0)
			p.mc_hists.append(mc_hist)
			
			p.log.setVariable(mc.name, 'filled', mc.tree.Draw('%s>>%s'%(var,hist_name), cut_string, 'goff'))
			
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
		
		if intsc:
			for mc_hist in p.mc_hists:
				mc_hist.Scale(dt_int/mc_int)
		
		# Kolmorogov test
		basemc = TH1F('hist_mc_ktbase', '', hbins, hmin, hmax)
		for mc_hist in p.mc_hists:
			basemc.Add(mc_hist)
		
		mc_max = basemc.GetMaximum()
		p.log.addParam('MC binmax', mc_max)
		
		p.log.addParam('Kolmogorov test', p.dt_hist.KolmogorovTest(basemc))
		
		# Stacking the histograms
		plot_title = '%s (%s)'%(var, plotname)
		if self.chstring is not None:
			plot_title += ' [' + str(self.chstring) + ']'
		p.stack = THStack('stack_%s'%plotname, plot_title)
		
		for ht in p.mc_hists:
			p.stack.Add(ht)
			
		p.stack.SetMaximum(1.1*max(data_max, mc_max))
		#p.stack.GetXaxis().SetTitle('This is the x-axis title. (GeV)')
		#p.stack.GetYaxis().SetTitle('This is the Y-axis title. (GeV)')
		
		# return the plot object where it can be drawn etc.
		return p

class _TTree(object):
	def __init__(self, fname):
		self.fname = fname
		
		print 'Open file: `%s`'%(fname)
		self.tfile = TFile(self.fname)
		
		if self.tfile.IsZombie():
			raise IOError('Error: file `%s` not found!'%fname)
		
		# We'll load all the trees
		keys = [x.GetName() for x in self.tfile.GetListOfKeys()]
		tree_names = filter(lambda x: x.startswith("trees"), keys)
		trees = [self.tfile.Get(k).Get("eventTree") for k in tree_names]
		for t in trees[1:]:
			trees[0].AddFriend(t)
		self.tree = trees[0]
	
	def getTotalEvents(self):
		return self.tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)

class _MCChannel(_TTree):
	def __init__(self, fname, crsec, name, color):
		super(_MCChannel, self).__init__(fname)
		
		self.crsec = crsec
		self.name = name
		self.color = color if color is not None else kOrange
		
		# Get the total number of events and return
		#N = tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)
		#return (tree, tfile, N)

class _DataChannel(_TTree):
	def __init__(self, fname, luminosity):
		super(_DataChannel, self).__init__(fname)
		self.luminosity = luminosity
		pass
 
class Plot:
	def __init__(self):
		self.log = PlotLog()
	
	def draw(self):
		self.stack.Draw('')
		self.dt_hist.Draw('E1 SAME')
		self.legend.Draw('SAME')
	
	def save(self, fout, w=550, h=400, log=True, fmt='png'):
		print 'Saving as:', fout+'.'+fmt
		cvs = TCanvas('', '', w, h)
		self.draw()
		cvs.SaveAs(fout+'.'+fmt)
		
		if log:
			self.log.save(fout+'.pylog')
