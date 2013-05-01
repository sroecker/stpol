import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy

file_list = [
#'/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1B_04_10/c9249c44a215ffeb8c9ba40f59092334/output_1_2_33N.root',
'/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1B_04_10/c9249c44a215ffeb8c9ba40f59092334/output_2_8_IvV.root'
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

nEv = 0
t0 = time.time()

nMuon_distr = []
for event in events:
    print nEv
    event.getByLabel(jetL, jetH)
    jets = jetH.product()
    if jetH.isValid():
        for jet in jets:
            pt,eta,phi = jet.pt(),jet.eta(),jet.phi()
        nJets = len(jets)

    try:
        event.getByLabel(eleL, eleH)
        if eleH.isValid():
            electrons = eleH.product()
            for ele in electrons:
                pt,eta,phi = ele.pt(),ele.eta(),ele.phi()
    except Exception as e:
        print e

    event.getByLabel(muL, muH)
    if muH.isValid():
        muons = muH.product()
        for muon in muons:
            pt,eta,phi = muon.pt(),muon.eta(),muon.phi()
        nMuons = len(muons)
        nMuon_distr.append(nMuons)

    nEv += 1
t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))
