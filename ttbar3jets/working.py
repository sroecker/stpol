# Run with python -i working.py [<filenames>, ...]
import sys
import ROOT
from ROOT import TH1F,THStack,TFile,TBrowser,TColor,TCanvas,TLegend

for fname in sys.argv[1:]:
	tfile = TFile(fname)
	if tfile.IsZombie():
		print 'Error opening file "%s"'%fname
		continue
	hist = tfile.Get('efficiencyAnalyzerMu').Get('muPath')
	tree = tfile.Get('treesCands').Get('eventTree')

	print 'File: ', fname
	for i in range(1,11):
		print "%2i: %f"%(i, hist.GetBinContent(i))
	print "Valid events:", tree.GetEntries('_recoTop_0_Mass==_recoTop_0_Mass')
	print
