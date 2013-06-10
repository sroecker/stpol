import ROOT
from DataFormats.FWLite import Events, Handle
import sys
import pdb
import cPickle
events = Events(sys.argv[1])

label = ("genParticles")
handle = Handle("std::vector<reco::GenParticle>")

def recurseDaughters(part):
    daug = []
    for n in range(part.numberOfDaughters()):
        daug.append(recurseDaughters(part.daughter(n)))
    if len(daug)==0:
        return [part.pdgId()]

def iterateDaughters(particles):
    partl = [p for p in particles]
    daugl = [map(lambda x: partl.index(x), [p.daughter(i) for i in range(p.numberOfDaughters())]) for p in particles]
    partl = [p.pdgId() for p in particles]
    return partl, daugl
n = 0

trees = []
for event in events:
    print n
    event.getByLabel(label, handle)
    if handle.isValid():
        particles = handle.product()
        trees.append(iterateDaughters(particles))
    n += 1
    if n==10:
        break

of = open("decay_tree.pickle", "w")
cPickle.dump(trees, of)
of.close()
