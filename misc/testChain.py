import ROOT

chain = ROOT.TChain("tree")
chain.Add("*.root")
proof = ROOT.TProof("workers=2")

chain.Draw(">>elist", "x>0.5")
elist = proof.GetOutputList().FindObject("elist")
