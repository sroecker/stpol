import ROOT
import time
from TestSelector import *

def myFunc(self, tree):
	vals = [tree._goodJets_0_Eta, tree._goodJets_1_Eta, tree._goodJets_2_Eta]
	vals.sort()
	#print "{0}".format(vals)
	return vals[1], 1

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
		tree.Draw('%s>>%s'%(v['var'],histname), cut)
		hs.append({'name': v['name'], 'var':v['var'], 'hist':h})
	
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

selector_t = time.clock()
selector_hs = drawWithSelector(tree, vs, '_goodJets_1_Eta>1')
selector_t = time.clock() - selector_t

normally_t = time.clock()
normally_hs = drawNormally(tree, vs, '_goodJets_1_Eta>1')
normally_t = time.clock() - normally_t

print 'Selector time:', selector_t
print 'Normally time:', normally_t

hs = map(lambda x,y: (x,y), selector_hs, normally_hs)

cvs=[]
for h in hs:
	cvs.append(ROOT.TCanvas('canvas_%s'%h[0]['name'], 'canvas_%s'%h[0]['name']))
	h[0]['hist'].Draw()
	h[1]['hist'].Draw('E1 SAME')
