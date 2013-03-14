import ROOT
import numpy
import random

f = ROOT.TFile("tree.root", "recreate")
tree = ROOT.TTree("tree", "My tree")
x = numpy.zeros(1, dtype=float)
tree.Branch("x", x, "normal/D")

for i in range(10000):
    x[0] = random.random()
    tree.Fill()

f.Write()
f.Close()
