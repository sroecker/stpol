import ROOT
from DataFormats.FWLite import Events, Handle, Lumis
import time
import numpy

file_list = [
#"sync/inclusive/step1_offlinepv_noSkim.root"
#"sync/pickevents.root"
"/hdfs/cms/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0059C6F3-7CDC-E111-B4CB-001A92811726.root"
]

events = Events(
    file_list
)

lumis = Lumis(
    file_list
)


recoMuH = Handle('std::vector<reco::Muon>')
recoMuL = ("muons")

vertexH = Handle('std::vector<reco::Vertex>')
vertexL = ("goodOfflinePrimaryVertices")

nEv = 0
t0 = time.time()

for event in events:

    print "event id =",event.object().id().event()

    event.getByLabel(recoMuL, recoMuH)
    if recoMuH.isValid():
        muons = recoMuH.product()
        nMu = 0
        for mu in muons:
            print recoMuL,nMu
            print "pt =",mu.pt()," eta =", mu.eta()
            try:
                print "globaltrack layers =",mu.globalTrack().hitPattern().trackerLayersWithMeasurement()
            except:
                print "invalid track"
            nMu += 1
    nEv += 1

t1 = time.time()
print "processing speed: %.2f events/sec" % (nEv / (t1-t0))
