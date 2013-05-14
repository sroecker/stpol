import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy

file_list = [
"/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1_04_19/c9249c44a215ffeb8c9ba40f59092334/output_1_1_VMY.root"
]

events = Events(
    file_list
)

lumis = Lumis(
    file_list
)

jetH = Handle ('std::vector <pat::Jet>')
jetL = ("smearedPatJetsWithOwnRef")

eleH = Handle('std::vector <pat::Electron>')
eleL = ("electronsWithID")

muH = Handle('std::vector <pat::Muon>')
muL = ("muonsWithID")

muH1 = Handle('edm::OwnVector<reco::Candidate,edm::ClonePolicy<reco::Candidate> >')
muL1 = ("muons1")

nEv = 0
t0 = time.time()


trigH = Handle("edm::TriggerResults")
nMuon_distr = []

def recurseMothers(particle):
    if particle.numberOfMothers()>0:
        return [particle.pdgId(), [recurseMothers(particle.mother(i)) for i in range(particle.numberOfMothers())]]
    else:
        return [particle.pdgId()]

def printTree(tree):
    if isinstance(tree, list):
        return "\n".join(map(printTree, tree[1:]))
    else:
        return ".%s" % str(tree)

def directMother(tree, notOf):
    parent1 = tree[1][0][0]
    if len(tree[1])>1:
        parent2 = tree[1][1][0]
    particle = tree[0]
    if abs(parent1)==notOf:
        return directMother(tree[1][0], notOf)
    else:
        return parent1

for event in events:
    #print "---"
    #print nEv
    event.getByLabel(muL, muH)
    muons = muH.product()
    if len(muons)>0:
        mu = muons[0]
        nGen = mu.genParticlesSize()
        l = None
        if nGen>0:
            l = recurseMothers(mu.genParticle(0))
            print l
            print directMother(l, 13)
    nEv += 1
t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))
