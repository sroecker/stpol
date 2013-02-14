import ROOT

from Selector import *

def myFunc(self, tree):
    vals = [tree._goodJets_0_Eta, tree._goodJets_1_Eta, tree._goodJets_2_Eta]
    vals.sort()
    #print "{0}".format(vals)
    return vals[1], 1

def drawWithSelector(tree, func, cut):
    Selector.func = func
    ROOT.gROOT.cd()
    tree.Draw(">>elist", cut)
    elist = ROOT.gROOT.Get("elist")
    tree.SetEventList(elist)
    
    h = ROOT.TH1F("hist", "hist", 20, 0, 5)
    Selector.hist = h
    def _func(selector, tree):
        return func(tree)
    Selector.func = _func
    tree.Process("TPySelector", "Selector")
    return h
    

file = ROOT.TFile("/Users/joosep/Documents/stpol/data/WD_Tbar_s.root")
tree = file.Get("treesJets").Get("eventTree")
h = drawWithSelector(tree, lambda tree: (tree._goodJets_1_Eta, 1.0), "_goodJets_1_Eta>1")
h.Draw()
