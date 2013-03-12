import ROOT
import time
from TestSelector import *

def drawWithSelector(tree, vs, cut):
	ROOT.gROOT.cd()
	tree.Draw(">>elist", cut)
	elist = ROOT.gROOT.Get("elist")
	tree.SetEventList(elist)
	
	hs=[]
	for v in vs:
		h = ROOT.TH1F("hist_%s"%v['name'], "hist_%s"%v['name'], 20, v['min'], v['max'])
		hs.append({'name': v['name'], 'var':v['var'], 'hist':h})
	
	TestSelector.hists = hs
	tree.Process("TPySelector", "TestSelector")
	
	return hs

def drawNormally(tree, vs, cut):
	hs=[]
	for v in vs:
		histname = 'hist_norm_%s' % v['name']
		h = ROOT.TH1F(histname, histname, 20, v['min'], v['max'])
		hs.append({'name': v['name'], 'var':v['var'], 'hist':h})
	
	t = time.clock()
	for v in vs:
		histname = 'hist_norm_%s' % v['name']
		tree.Draw('%s>>%s'%(v['var'],histname), cut, 'goff')
	print 'Time normally:', time.clock()-t
	
	return hs

tfile = ROOT.TFile("/home/joosep/singletop/data/trees/Feb18/Iso/SingleEleC1_495_pb.root")
# We'll load all the trees
keys = [x.GetName() for x in tfile.GetListOfKeys()]
tree_names = filter(lambda x: x.startswith("trees"), keys)
trees = [tfile.Get(k).Get("eventTree") for k in tree_names]
for t in trees[1:]:
	trees[0].AddFriend(t)
tree = trees[0]

vs = [
	{'name': 'mass', 'var': '_recoTop_0_Mass', 'min': 0, 'max': 500},
	{'name': 'eta',  'var': '_goodJets_1_Eta', 'min': 0, 'max': 5}
]

#cut = '1 == 1'
cut = '_goodJets_1_Eta>1 && _recoTop_0_Mass<400'

normally_t = time.clock()
normally_hs = drawNormally(tree, vs, cut)
normally_t = time.clock() - normally_t

selector_t = time.clock()
selector_hs = drawWithSelector(tree, vs, cut)
selector_t = time.clock() - selector_t

normlist_t = time.clock()
normally_hs = drawNormally(tree, vs, '')
normlist_t = time.clock() - normlist_t

print
print 'Selector time:', selector_t
print 'Normally time:', normally_t
print 'Normlist time:', normlist_t

hs = map(lambda x,y: (x,y), selector_hs, normally_hs)

cvs=[]
for h in hs:
	cvs.append(ROOT.TCanvas('canvas_%s'%h[0]['name'], 'canvas_%s'%h[0]['name']))
	h[1]['hist'].Draw()
	h[0]['hist'].Draw('E1 SAME')
