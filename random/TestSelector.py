import ROOT

class TestSelector(ROOT.TPySelector):
	def __init__(self):
		self.nProcessed = 0
	
	def setHist(self, hist):
		hist = hist
	
	def setFunc(self, func):
		func = func
	
	def Begin( self ):
		print 'py: beginning'
	def SlaveBegin( self, tree ):
		print 'py: slave beginning'
		
	def Process( self, entry ):
		self.nProcessed += 1
		mytree=self.fChain
		mytree.GetEntry( entry )
		
		for h in self.hists:
			(val, weight) = (getattr(mytree, h['var']), 1.0)
			h['hist'].Fill(val, weight)
		
		return 1
	
	def SlaveTerminate( self ):
		pass
	def Terminate( self ):
		print "Processed {0} events".format(self.nProcessed)
