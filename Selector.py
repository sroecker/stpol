import ROOT

class Selector( ROOT.TPySelector ):

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
        
        (val, weight) = Selector.func(self, mytree)
        Selector.hist.Fill(val, weight)
        
        return 1
    
    def SlaveTerminate( self ):
        pass
    def Terminate( self ):
        print "Processed {0} events".format(self.nProcessed)