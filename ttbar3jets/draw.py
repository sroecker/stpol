import argparse
import ROOT
from ROOT import TH1F,TFile,TCanvas,TLegend

# Data parameters
totalDataEvents = 5363303 # from DAS
totalLuminosity = 808.472 # 1/pb, from TWiki
ttbarCrossSection = 136.3 # pb, from PREP

# Extra parameters from arguments:
parser = argparse.ArgumentParser(description='Plots MC and Data for some variable.')
parser.add_argument('tree')
parser.add_argument('var')
parser.add_argument('mc') # MC root file
parser.add_argument('data') # DATA root file
parser.add_argument('--hist', type=float,
                    nargs=2, metavar=('min', 'max'),
                    help='min and max boundary values for the histogram')
parser.add_argument('--bins', type=int, default=16,
                    help='number of histogram bins')
parser.add_argument('--save', help='save the histogram to a file')
parser.add_argument('-b', action='store_true',
                    help='run in batch mode. Requires --save.')

args = parser.parse_args() # if the arguments are syntactically invalid, the script stops here

# Check for batch mode
if args.b and args.save is not None:
	print 'Running in batch mode.'
elif args.b and args.save is None:
	print 'Error: Batch mode requires an output file!'
	exit(-1)

# Open root files and get respective trees:
def openTree(fname, treename):
	print 'Open: from file `%s` tree `%s`.'%(fname, treename)
	tfile = TFile(fname)
	if tfile.IsZombie():
		raise Exception('Error opening file "%s"!'%fname)
	tree = tfile.Get(treename).Get('eventTree')
	N = tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)
	return (tree, tfile, N)
(tree_mc, tfile_mc, N_mc) = openTree(args.mc, args.tree)
(tree_dt, tfile_dt, N_dt) = openTree(args.data, args.tree)

print 'Drawing variable `%s`' % args.var

# extract histogram parameters
hist_bins = args.bins
hist_min = min(tree_mc.GetMinimum(args.var), tree_dt.GetMinimum(args.var)) if args.hist is None else args.hist[0]
hist_max = max(tree_mc.GetMaximum(args.var), tree_dt.GetMaximum(args.var)) if args.hist is None else args.hist[1]

# Histograms
title = '%s.%s' % (args.tree, args.var)

hist_mc   = TH1F('hist_mc', title, hist_bins, hist_min, hist_max)
print 'Filling MC. Events:   ', tree_mc.Draw('%s>>hist_mc'%args.var, '{0}=={0}'.format(args.var), 'goff')

hist_dt   = TH1F('hist_dt', title, hist_bins, hist_min, hist_max)
print 'Filling data. Events: ', tree_dt.Draw('%s>>hist_dt'%args.var, '{0}=={0}'.format(args.var), 'goff')

# MC scaling
effective_lumi = totalLuminosity*float(N_dt)/float(totalDataEvents)
#effective_lumi = totalLuminosity
expectedEvents = ttbarCrossSection*effective_lumi
scale_factor = float(expectedEvents)/float(N_mc)
hist_mc.Scale(scale_factor)

print 'Initial MC events:   %8d' % N_mc
print 'Initial data events: %8d' % N_dt
print 'Total data events:   %8d' % totalDataEvents

print 'Luminosity:      %8.2f' % totalLuminosity
print 'Eff, luminosity: %8.2f' % effective_lumi
print 'Expected events:     %8d' % expectedEvents
print 'Cross section:   %8.2f' % ttbarCrossSection
print 'Scaling factor:  %f' % scale_factor


hist_dt.SetMarkerStyle(20)
hist_mc.SetFillColor(ROOT.kOrange + 7)
hist_mc.SetLineWidth(0)

canvas = TCanvas()
if N_mc >= N_dt:
	hist_mc.Draw('')
	hist_dt.Draw('E1 SAME')
else:
	hist_dt.Draw('E1')
	hist_mc.Draw('SAME')

# Save the canvas:
if args.save is not None:
	print 'Saving to: %s'%args.save
	canvas.SaveAs(args.save)
	if not args.b:
		raw_input('Press enter to close')
else:
	print 'Enter filename to save or leave empty to exit.'
	fout = raw_input('Filename: ')
	if len(fout) > 0:
		canvas.SaveAs(fout)

