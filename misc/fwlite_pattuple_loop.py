import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy

file_list = [
    "/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1B_04_10/c9249c44a215ffeb8c9ba40f59092334/output_90_1_t5g.root",
    "/hdfs/cms/store/user/joosep/T_t-channel_TuneZ2star_8TeV-powheg-tauola/stpol_step1B_04_10/c9249c44a215ffeb8c9ba40f59092334/output_7_3_YPN.root",
#"/Users/joosep/Documents/stpol/data/output_1_2_33N.root"
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


trigH = Handle("edm::TriggerResults")
nMuon_distr = []
for event in events:
    print "---"
    print nEv
    #if nEv>100:

    #    break
    #event.getByLabel(("TriggerResults", "", "HLT"), trigH)
    #trigs = trigH.product()
    #trignames = trigs.getTriggerNames()
    #print "ntrig = %d" % len(trignames)
    #for trig in trignames:
    #    s = str(trig)
    #    print s
    #    #if s.startswith("HLT_IsoMu24_eta2p1_v"):
    #    #    print s

    n_jets = -1
    try:
        event.getByLabel(jetL, jetH)

        if jetH.isValid():
            jets = jetH.product()
            n_jets = len(jets)
            for jet in jets:
                pt,eta,phi = jet.pt(),jet.eta(),jet.phi()
            nJets = len(jets)
    except Exception as e:
    #    jetH = Handle ('std::vector <pat::Jet>')
        print str(e)
        break

    n_eles = -1
    try:
        event.getByLabel(eleL, eleH)
        if eleH.isValid():
            electrons = eleH.product()
            n_eles = len(electrons)
            for ele in electrons:
                pt,eta,phi = ele.pt(),ele.eta(),ele.phi()
    except Exception as e:
    #    eleH = Handle('std::vector <pat::Electron>')
        print str(e)
        break

    n_muons = -1
    try:
        event.getByLabel(muL, muH)
        if muH.isValid():
            muons = muH.product()
            n_muons = len(muons)
            for muon in muons:
                pt,eta,phi = muon.pt(),muon.eta(),muon.phi()
            nMuons = len(muons)
            nMuon_distr.append(nMuons)
    except Exception as e:
    #    muH = Handle('std::vector <pat::Muon>')
        print str(e)
        break

    nEv += 1
    print n_jets, n_eles, n_muons

t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))
