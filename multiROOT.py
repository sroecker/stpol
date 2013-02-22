import ROOT
import multiprocessing
import pickle

def getEntries(cut):
    fi = ROOT.TFile("~/singletop/data/trees/T_t.root", "READ")
    t = fi.Get("treesDouble").Get("eventTree")
    t.Draw("cosThetaLightJet_cosTheta>>hist", cut, "goff")
    hist = fi.Get("hist")
    return pickle.dumps(hist)

if __name__=="__main__":
    ROOT.gStyle.SetPalette(1) #need to call gStyle object to notify ROOT's lazy initializer

    cuts = ["cosThetaLightJet_cosTheta>0", "cosThetaLightJet_cosTheta<0", "cosThetaLightJet_cosTheta>0 && cosThetaLightJet_cosThetaProducerTrueAll!=cosThetaLightJet_cosThetaProducerTrueAll"]

    p = multiprocessing.Pool(2)

    out = map(pickle.loads, p.map(getEntries, cuts))
    print out
