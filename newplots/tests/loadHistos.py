import ROOT
from bTagWeightValid2 import Histogram
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///histos.db')
Session = sessionmaker(bind=engine)
session = Session()
#Base.metadata.create_all(engine)

hists = []
sample = "TTJets_FullLept"
for hist in session.query(Histogram).\
            filter(Histogram.sample_name==sample).\
            filter(Histogram.var=="b_weight_nominal").\
            filter((Histogram.cut=="n_tags==0.0") | (Histogram.cut=="n_tags==0.0 && true_b_count==0.0") | (Histogram.cut=="n_tags==0.0 && true_b_count==1.0") | (Histogram.cut=="n_tags==0.0 && true_b_count==2.0") | (Histogram.cut=="n_tags==0.0 && true_b_count==3.0")).\
            order_by(Histogram.id):
    hist.loadFile()
    hists.append(hist)
    print hist

first = True
colors = [ROOT.kBlack, ROOT.kRed, ROOT.kBlue, ROOT.kGreen, ROOT.kMagenta]
leg = ROOT.TLegend(0.8, 0.3, 0.96, 0.8)
leg.SetFillColor(ROOT.kWhite)
c = ROOT.TCanvas("c")
c.SetLogy()
names = ["0_tags", "true_b_0", "true_b_1", "true_b_2", "true_b_3"]
titles = ["any number of b-jets", "0 true b-jets", "1 true b-jets", "2 true b-jets", "3 true b-jets"]
i = 0
for h in hists:
    h.hist.SetName(names[i])
    h.hist.SetTitle(titles[i])
    i += 1

hists[0].hist.GetXaxis().SetTitle("b-weight (nominal)")
hists[0].hist.GetYaxis().SetRangeUser(1, 10**5)
for h in hists:
    color = colors.pop()
    h.hist.Rebin(2)
    print "%s: %.2f" % (h.hist.GetName(), h.hist.Integral())
#    if(h.hist.Integral()>0):
#        h.hist.Scale(1.0/h.hist.Integral())
    h.hist.SetLineColor(color)
    h.hist.SetFillColor(color)
    h.hist.SetFillStyle(3005)
    if first:
        h.hist.Draw("H")
        h.hist.SetStats(False)
    else:
        h.hist.Draw("SAME H")
    leg.AddEntry(h.hist, h.hist.GetTitle())
    first = False
    #print (h.hist.Integral()*h.hist.GetMean())
leg.Draw()
hists[0].hist.SetTitle(sample + " b-weight distributions")
#c.SetRightMargin(0.3)
c.SaveAs("bWeightDistributions.pdf")
