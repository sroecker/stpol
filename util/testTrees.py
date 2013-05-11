import ROOT
import glob
import sys

for f in glob.glob(sys.argv[1]):
    if not f.endswith(".root"):
        continue
    fi = ROOT.TFile(f)
    if fi.IsZombie() == True:
        print f + " is broken!"
    fi.Close()
