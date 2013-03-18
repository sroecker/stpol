import ROOT

chain = ROOT.TChain("tree")
chain.Add("*.root")
proof = ROOT.TProof.Open("workers=8")
chain.SetProof(True)
chain.Draw(">>elist", "x>0.5", "entrylist")
elist = proof.GetOutputList().FindObject("elist")
if not elist:
    print "Error getting entry list: elist=" + str(elist)
else:
    print elist.GetN()
