# Run with python -i working.py [<filenames>, ...]
import sys
import ROOT
from ROOT import TFile

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

for fname in sys.argv[1:]:
	tfile = TFile(fname)
	if tfile.IsZombie():
		print 'Error opening file "%s"'%fname
		continue
	hist = tfile.Get('efficiencyAnalyzerMu').Get('muPath')
	#tree = tfile.Get('treesCands').Get('eventTree')
	#tree.AddFriend(tfile.Get('treesJets').Get('eventTree'))
	#tree.AddFriend(tfile.Get('treesJets').Get('eventTree'))
	
	# We'll load all the trees
	keys = [x.GetName() for x in tfile.GetListOfKeys()]
	tree_names = filter(lambda x: x.startswith("trees"), keys)
	trees = [tfile.Get(k).Get("eventTree") for k in tree_names]
	for t in trees[1:]:
		trees[0].AddFriend(t)
	tree = trees[0]

	print 'File: ', fname
	print 'Number of bins:', hist.GetSize()
	for i in range(1,hist.GetSize()):
		print "%2i: %s (%s)"%(i, th_sep(hist.GetBinContent(i)), hist.GetXaxis().GetBinLabel(i))
	
	print 'Event total:', th_sep(tree.GetEntries())
	print 'Events where _topCount==1:', th_sep(tree.GetEntries('_topCount==1'))
	print "_muonCount:", th_sep(tree.GetEntries('_topCount==1 && _muonCount==1'))
	print "_bJetCount:", th_sep(tree.GetEntries('_topCount==1 && _bJetCount==1'))
	print "_lightJetCount:", th_sep(tree.GetEntries('_topCount==1 && _lightJetCount==2'))
	print "PU cuts:", th_sep(tree.GetEntries('(_topCount == 1)&&(_goodJets_0_Pt>60)&&(_goodJets_1_Pt>60)&&(_muAndMETMT>50)&&(_untaggedJets_0_rms<0.025)'))
	print
