import sys
import ROOT

def geth(fn):
    f = ROOT.TFile(fn)
    h = f.Get("efficiencyAnalyzerMu").Get("muPath")
    ROOT.gROOT.cd()
    h1 = h.Clone()
    return h1

files = [
"step2_trees_1_1_5tX.root",
"step2_trees_2_1_CBY.root",
"step2_trees_3_1_uLa.root",
"step2_trees_4_1_eba.root"
]

hists = map(geth, files)
print hists
