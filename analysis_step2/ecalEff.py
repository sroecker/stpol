import ROOT
import sys

f = ROOT.TFile(sys.argv[1])
t = f.Get("treesMu").Get("eventTree")
t.AddFriend(f.Get("treesEle").Get("eventTree"))
t.AddFriend(f.Get("treesBool").Get("eventTree"))
failEcal = t.GetEntries("_ecalLaserCorrFilter==0 && goodSignalMuons_0_Pt==goodSignalMuons_0_Pt")
passEcal = t.GetEntries("_ecalLaserCorrFilter==1 && goodSignalMuons_0_Pt==goodSignalMuons_0_Pt")
frac = float(failEcal)/(float(failEcal)+float(passEcal))

totalEvents = f.Get("efficiencyAnalyzerMu").Get("muPath").GetBinContent(1)
passedEvents = f.Get("efficiencyAnalyzerMu").Get("muPath").GetBinContent(10)
print "%.4f%% events fail ECAL filter out of %d passed (%d processed)" % (100.0*frac, passedEvents, totalEvents)
