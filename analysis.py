import ROOT
ROOT.gROOT.SetBatch(True)

f = ROOT.TFile("out_step3_trees.root")
print f
trees = dict()

trees["jets"] = f.Get("treesJets").Get("eventTree")
trees["muons"] = f.Get("treesMu").Get("eventTree")

t = trees["jets"]
t.AddFriend(trees["muons"])
ROOT.gROOT.cd()
t.Draw("abs(goodJets_0_Eta)>>h0")
t.Draw("abs(goodJets_1_Eta)>>h1")