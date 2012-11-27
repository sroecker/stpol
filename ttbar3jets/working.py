# Run with python -i working.py <filename>
import sys
import ROOT
from ROOT import TH1F,THStack,TFile,TBrowser,TColor,TCanvas,TLegend

fname = sys.argv[1]

# Configuration
#fname = 'stpol_TTBar_3J1T_numEvent1000000_trees.root'
tfile = TFile(fname)
if tfile.IsZombie():
	print 'Error opening file'
	exit()
hist = tfile.Get('efficiencyAnalyzerMu').Get('muPath')
tree = tfile.Get('treesCands').Get('eventTree')

print 'File: ', fname
for i in range(1,11):
	print "%2i: %f"%(i, hist.GetBinContent(i))
print "Valid events:", tree.GetEntries('_recoTop_0_Mass==_recoTop_0_Mass')
