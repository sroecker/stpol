import ROOT
import copy
from plots.common.cuts import Cuts, Cut

filename="inclusive/out_step3.root"
channel="mu"
samp = ROOT.TFile(filename)
tree = samp.Get("trees/Events")
vals = []

if channel=="mu":
    cut = Cuts.hlt_isomu
    vals.append(tree.GetEntries(str(cut)))
    cut = cut * Cut("n_muons==1")
    vals.append(tree.GetEntries(str(cut)))
elif channel=="ele":
    cut = Cuts.hlt_isoele
    vals.append(tree.GetEntries(str(cut)))
    cut = cut * Cut("n_eles==1")
    vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_veto_mu==0")
vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_veto_ele==0")
cut_aftermu = copy.deepcopy(cut)
vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_jets==2")
vals.append(tree.GetEntries(str(cut)))

if channel=="mu":
    cut = cut * Cut("mt_mu>=45")
    vals.append(tree.GetEntries(str(cut)))
elif channel=="ele":
    cut = cut * Cut("met>=35")
    vals.append(tree.GetEntries(str(cut)))

cut = cut * Cut("n_tags==1")
vals.append(tree.GetEntries(str(cut)))

print vals
vals = map(str, vals)
print " | ".join(vals)
