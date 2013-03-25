enabledSamples = {"WJets": "WD_WJets1.root", "W1Jets": "W1Jets.root"}
from anfw import *

cutAmu = (Cuts.mu + Cuts.jets_2plusJ + Cuts.jetPt + Cuts.jetRMS + Cuts.MTmu + Cuts.mlnu + Cuts.etaLJ)
cutAele = (Cuts.ele + Cuts.jets_2plusJ + Cuts.jetPt + Cuts.jetRMS + Cuts.MTele + Cuts.mlnu + Cuts.etaLJ)
cutBmu = (Cuts.mu + Cuts.jets_2J1T + Cuts.jetPt + Cuts.jetRMS + Cuts.MTmu + Cuts.mlnu + Cuts.etaLJ)
cutBele = (Cuts.ele + Cuts.jets_2J1T + Cuts.jetPt + Cuts.jetRMS + Cuts.MTele + Cuts.mlnu + Cuts.etaLJ)

samples = ["W1Jets", "WJets"]
channels = loadSamples(enabledSamples)

counts = dict()
counts["W1Jets"] = dict()
counts["WJets"] = dict()
counts["W1Jets"]["mu"] = dict()
counts["W1Jets"]["ele"] = dict()
counts["WJets"]["mu"] = dict()
counts["WJets"]["ele"] = dict()
for samp in samples:
    print samp
    mu_2plusJ = channels[samp].tree.GetEntries(cutAmu.cutStr)
    ele_2plusJ = channels[samp].tree.GetEntries(cutAele.cutStr)
    mu_2J1T = channels[samp].tree.GetEntries(cutBmu.cutStr)
    ele_2J1T = channels[samp].tree.GetEntries(cutBele.cutStr)
    counts[samp]["mu"]["2plusJ"] = mu_2plusJ
    counts[samp]["ele"]["2plusJ"] = ele_2plusJ
    counts[samp]["mu"]["2J1T"] = mu_2J1T
    counts[samp]["ele"]["2J1T"] = ele_2J1T
print counts
