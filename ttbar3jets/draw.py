import argparse
import ROOT
from ROOT import TH1F,TFile,TCanvas,TLegend,TText

def th_sep(i, sep=','):
	i = abs(int(i))
	o = []
	while i > 0:
		o.append(i%1000)
		i /= 1000
	o.reverse()
	return str(sep).join([str(o[0])] + map(lambda x: '%03d'%x, o[1:]))

# Data parameters
totalDataEvents = 5363303 # from DAS
totalLuminosity = 808.472 # 1/pb, from TWiki
ttbarCrossSection = 234 # pb, from AN

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
parser.add_argument('-i', '--info', action='store_true',
                    help='create another pad with important values and variables')
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

# Remove statistics boxes from histograms
hist_mc.SetStats(False)
hist_dt.SetStats(False)

# Drawing
if args.info:
	canvas = TCanvas('canvas', 'Plot of `%s`'%args.var, 700, 800)
	upperPad = ROOT.TPad('graph', '', 0.005, 0.420, 0.995, 0.995)
	upperPad.Draw()
	lowerPad = ROOT.TPad('text',  '', 0.020, 0.005, 0.995, 0.420)
	lowerPad.Draw()

	upperPad.cd()
	hist_mc.Draw('')
	hist_dt.Draw('E1 SAME')

	lowerPad.cd()
	texts = [
		TText(0.0, 0.95, 'Variable: %s' % (args.var)),
		TText(0.0, 0.90, 'Lumi / cr.sec / exp.ev = %.2f / %.2f / %.2f' % (totalLuminosity, ttbarCrossSection, expectedEvents)),
		TText(0.0, 0.85, 'Total events (mc / data): %s / %s' % (th_sep(N_mc), th_sep(N_dt))),
		TText(0.0, 0.80, 'Filled events (mc / data): %d / %d' % (filled_N_mc, filled_N_dt)),
		TText(0.0, 0.75, 'MC scaling factor / scaled events: %.5f / %.2f' % (scale_factor, scale_factor*filled_N_mc)),
		TText(0.0, 0.65, 'Cuts (&&-ed together):')
	]
	
	y=0.60; dy=-0.05
	for s in cuts:
		texts.append(TText(0.0, y, '       ' + s))
		y += dy
	
	for t in texts:
		t.Draw()
	
	lowerPad.Modify()
	upperPad.Modify()
	canvas.Update()
else:
	canvas = TCanvas('canvas', 'Plot of `%s`'%args.var)
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

