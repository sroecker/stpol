import ROOT
import sys
import argparse
import fnmatch

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--infile', type=str, default="/scratch/joosep/step2_MC_Iso_Mar14/WD_T_t/res/output_1_1_SfY.root")
parser.add_argument('-b', '--brmatch', type=str, default="*")
args = parser.parse_args()

f = ROOT.TFile(args.infile)
tree = f.Get("Events")

branches = [br.GetName() for br in tree.GetListOfBranches()]

filtered_branches = filter(lambda x: fnmatch.fnmatch(x, args.brmatch), branches)

for b in filtered_branches:
    print b
