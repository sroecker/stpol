import re
import ROOT
from ROOT import TH1F,THStack,TFile,TBrowser,TColor,TCanvas,TLegend

# Configuration
#fname_mc = 'stpol_TTBar_3J1T_numEvent10000_trees.root'
fname_mc = 'stpol_TTBar_3J1T_numEvent1000000_trees.root'
#fname_data = 'stpol_Data_3J1T_numEvent15000_trees.root'
fname_data = 'stpol_Data_3J1T_numEvent120000_trees.root'

var_class = 'treesCands'; var_name = '_recoTop_0_Mass'
check_name = '_topCount'
hist_min = 0; hist_max = 1000; hist_bins = 20;

title = 'topMass'

def fillHistogram(hist, fname, varclass, varname, checkname):
	print 'Filling histogram using "%s"'%fname
	
	tfile = TFile(fname)
	if tfile.IsZombie():
		print 'Error opening file "%s"!'%fname
		exit()
	
	tree_var  = tfile.Get(varclass).Get('eventTree')
	tree_chck = tfile.Get('treesInt').Get('eventTree')
	
	entries = tree_var.GetEntries()
	print 'Entries:', tree_var.GetEntries(), tree_chck.GetEntries()
	
	N = 0
	for i in range(entries):
		tree_var.GetEntry(i)
		tree_chck.GetEntry(i)

		if getattr(tree_chck, checkname) > 0:
			#print '%3i Top: %6.2f (%2i)' % (i, getattr(tree_var, varname), getattr(tree_chck, checkname))
			hist.Fill(getattr(tree_var, varname))
			N += 1
	return N

hist_mc   = TH1F('AAA', title, hist_bins, hist_min, hist_max)
N_mc = fillHistogram(hist_mc, fname_mc, var_class, var_name, check_name)
print 'MC datapoints  : %i' % N_mc

hist_data = TH1F('', '', hist_bins, hist_min, hist_max)
N_data = fillHistogram(hist_data, fname_data, var_class, var_name, check_name)
print 'Data datapoints: %i' % N_data

hist_mc.Scale(float(N_data)/float(N_mc))

hist_data.SetMarkerStyle(20)
hist_mc.SetFillColor(ROOT.kOrange + 7)
hist_mc.SetLineWidth(0)

canvas = TCanvas()
hist_mc.Draw('')
hist_data.Draw('E1 SAME')
#canvas.SaveAs('plot.pdf')
