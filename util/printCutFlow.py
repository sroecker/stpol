import ROOT
import sys

files = sys.argv[1:]
for fi in files:
    f = ROOT.TFile(fi)
    hi = f.Get("efficiencyAnalyzerMu").Get("muPath")
    print "%d %s" % (hi.GetBinContent(1), fi)
    f.Close()
