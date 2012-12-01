import argparse
import ROOT
from ROOT import TH1F,TFile,TCanvas,TLegend

# Data parameters
totalDataEvents = 5363303 # from DAS
totalLuminosity = 808.472 # 1/pb, from TWiki
ttbarCrossSection = 136.3 # pb, from PREP

# Extra parameters from arguments:
parser = argparse.ArgumentParser(description='Plots MC and Data for some variable.')
parser.add_argument('var')
parser.add_argument('mc') # MC root file
parser.add_argument('data') # DATA root file
parser.add_argument('-c', '--cut', action='append', default=[],
                    help='additional cuts')
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
def openTree(fname):
	print 'Open file: `%s`'%(fname)
	tfile = TFile(fname)
	if tfile.IsZombie():
		raise Exception('Error opening file "%s"!'%fname)
	
	# We'll load all the trees
	keys = [x.GetName() for x in tfile.GetListOfKeys()]
	tree_names = filter(lambda x: x.startswith("trees"), keys)
	trees = [tfile.Get(k).Get("eventTree") for k in tree_names]
	for t in trees[1:]:
		trees[0].AddFriend(t)
	tree = trees[0]
	
	# Get the total number of events and return
	N = tfile.Get('efficiencyAnalyzerMu').Get('muPath').GetBinContent(1)
	return (tree, tfile, N)
(tree_mc, tfile_mc, N_mc) = openTree(args.mc)
(tree_dt, tfile_dt, N_dt) = openTree(args.data)

print 'Drawing variable `%s`' % args.var

# extract histogram parameters
hist_bins = args.bins
hist_min = min(tree_mc.GetMinimum(args.var), tree_dt.GetMinimum(args.var)) if args.hist is None else args.hist[0]
hist_max = max(tree_mc.GetMaximum(args.var), tree_dt.GetMaximum(args.var)) if args.hist is None else args.hist[1]

# Histograms
title = '%s' % (args.var)

# Additional cuts applied
cuts = ['_topCount==1'] + args.cut
cuts_str = '&&'.join(map(lambda s: '('+str(s)+')', cuts))
print 'Cuts applied:'
for c in cuts:
	print '>', c
print 'Cuts string: `%s`' % cuts_str
print

# Creating the histograms
hist_mc   = TH1F('hist_mc', title, hist_bins, hist_min, hist_max)
filled_N_mc = tree_mc.Draw('%s>>hist_mc'%args.var, cuts_str, 'goff')

hist_dt   = TH1F('hist_dt', title, hist_bins, hist_min, hist_max)
filled_N_dt = tree_dt.Draw('%s>>hist_dt'%args.var, cuts_str, 'goff')

# MC scaling
effective_lumi = totalLuminosity*float(tree_dt.GetEntries())/float(totalDataEvents)
expectedEvents = ttbarCrossSection*effective_lumi
scale_factor = float(expectedEvents)/float(N_mc)
hist_mc.Scale(scale_factor)

# Some verbosity...
print 'Filled MC events:      %8d' % filled_N_mc
print 'Filled data events:    %8d' % filled_N_dt
print 'Initial MC events:     %8d' % N_mc
print 'Initial data events:   %8d' % N_dt
print 'Events with top (MC):  %8d' % tree_mc.GetEntries('_topCount==1')
print 'Events with top (DT):  %8d' % tree_dt.GetEntries('_topCount==1')
print 'Events with cuts (MC): %8d' % tree_mc.GetEntries(cuts_str)
print 'Events with cuts (DT): %8d' % tree_dt.GetEntries(cuts_str)
print 'Total data events:     %8d' % totalDataEvents
print

print 'Luminosity:            %8.2f' % totalLuminosity
print 'Eff, luminosity:       %8.2f' % effective_lumi
print 'Expected events:       %8d' % expectedEvents
print 'Cross section:         %8.2f' % ttbarCrossSection
print 'Scaling factor:        %f' % scale_factor
print

hist_dt.SetMarkerStyle(20)
hist_mc.SetFillColor(ROOT.kOrange + 7)
hist_mc.SetLineWidth(0)

# y-axis scaling (with 10% margin)
ymax = int(1.1 * max(hist_mc.GetMaximum(), hist_dt.GetMaximum()))
hist_mc.SetMaximum(ymax)
hist_dt.SetMaximum(ymax)

canvas = TCanvas()
hist_mc.Draw('')
hist_dt.Draw('E1 SAME')

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

