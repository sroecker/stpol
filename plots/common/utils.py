import ROOT

def lumi_textbox(lumi, pos="top-center"):
    if pos=="top-center":
        coords = [0.2, 0.86, 0.66, 0.91]
    text = ROOT.TPaveText(coords[0], coords[1], coords[2], coords[3], "NDC")
    text.AddText("CMS preliminary #sqrt{s} = 8 TeV, #int L dt = %.1f fb^{-1}" % (float(lumi)/1000.0))
    text.SetShadowColor(ROOT.kWhite)
    text.SetLineColor(ROOT.kWhite)
    text.SetFillColor(ROOT.kWhite)
    text.Draw()
    return text