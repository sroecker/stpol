import ROOT
from ROOT import TFile,TH1F,THStack,TPad,TCanvas,TLegend,TText

def th_sep(i, sep=','):
	i = abs(int(i))
	if i == 0:
		return '0'
	o = []
	while i > 0:
		o.append(i%1000)
		i /= 1000
	o.reverse()
	return str(sep).join([str(o[0])] + map(lambda x: '%03d'%x, o[1:]))

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
		print 'Plotting %s'%var
		print 'Histogram: %f - %f (%d)'%(hmin, hmax, hbins)
		p = Plot()
		
		cut_string = self._getCutString()
		print 'Cut string:', cut_string
		
		# Create the legend
		p.legend = TLegend(0.80, 0.65, 1.00, 0.90)
		
		# Create histograms
		p.dt_hist = TH1F('hist_data', '', hbins, hmin, hmax)
		p.dt_hist.SetMarkerStyle(20)
		print 'Filled (data):', self._data.tree.Draw('%s>>hist_data'%var, cut_string, 'goff')
		dt_int = p.dt_hist.Integral()
		print 'int (data):', dt_int
		
		#effective_lumi = self._data.luminosity*float(self._data.tree.GetEntries())/float(self._data.getTotalEvents())
		# TODO: implement effectice luminosity
		effective_lumi = self._data.luminosity
		
		data_max = p.dt_hist.GetMaximum()
		
		mc_int = 0
		p.mc_hists = []
		for mc in self._mcs:
			hist_name = 'hist_%s_mc_%s'%(plotname, mc.name)
			
			mc_hist = TH1F(hist_name, '', hbins, hmin, hmax)
			mc_hist.SetFillColor(mc.color)
			mc_hist.SetLineWidth(0)
			p.mc_hists.append(mc_hist)
			
			print 'Filled (%s):'%hist_name, mc.tree.Draw('%s>>%s'%(var,hist_name), cut_string, 'goff')
			
			# MC scaling
			expected_events = mc.crsec*effective_lumi
			total_events = mc.getTotalEvents()
			scale_factor = float(expected_events)/float(total_events)
			mc_hist.Scale(scale_factor)
			
			p.legend.AddEntry(mc_hist, mc.name, 'F')
			
			mc_int += mc_hist.Integral()
			print 'totev (%s):'%mc.name, total_events
			print 'expev (%s):'%mc.name, expected_events
			print 'scf (%s):'%mc.name, scale_factor
			print 'int (%s):'%mc.name, mc_int
		
		if intsc:
			for mc_hist in p.mc_hists:
				mc_hist.Scale(dt_int/mc_int)
		
		# Kolmorogov test
		basemc = TH1F('hist_mc_ktbase', '', hbins, hmin, hmax)
		for mc_hist in p.mc_hists:
			basemc.Add(mc_hist)
		print 'Kolmogorov test:', p.dt_hist.KolmogorovTest(basemc)
		
		mc_max = basemc.GetMaximum()
		
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
		pass
	
	def draw(self):
		self.stack.Draw('')
		self.dt_hist.Draw('E1 SAME')
		self.legend.Draw('SAME')
	
	def save(self, fout, w=550, h=400):
		print 'Saving as:', fout
		cvs = TCanvas('', '', w, h)
		self.draw()
		cvs.SaveAs(fout)
