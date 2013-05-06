import ROOT
from odict import OrderedDict as dict

#Here the latter items will become topmost in stacks
merge_cmds = dict()
merge_cmds["data"] = ["SingleMuAB", "SingleMuC", "SingleMuD"]
merge_cmds["diboson"] = ["WW", "WZ", "ZZ"]
merge_cmds["W(#rightarrow l #nu) + jets"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]
merge_cmds["DY-jets"] = ["DYJets"]
merge_cmds["t#bar{t}"] = ["TTJets_FullLept", "TTJets_SemiLept"]
merge_cmds["tW-channel"] = ["T_tW", "Tbar_tW"]
merge_cmds["s-channel"] = ["T_s", "Tbar_s"]
merge_cmds["t-channel"] = ["T_t", "Tbar_t"]

def lumi_textbox(lumi, pos="top-left"):
    """
    This method creates and draws the "CMS Preliminary" luminosity box,
    displaying the lumi in 1/fb and the COM energy.
    
    **Mandatory arguments:
    lumi - the integrated luminosity in 1/pb
    
    **Optional arguments:
    pos - a string specifying the position of the lumi box.
    
    **returns:
    A TPaveText instance with the lumi information
    """
    if pos=="top-left":
        coords = [0.2, 0.86, 0.66, 0.91]
    if pos=="top-right":
        coords = [0.5, 0.86, 0.96, 0.91]

    text = ROOT.TPaveText(coords[0], coords[1], coords[2], coords[3], "NDC")
    text.AddText("CMS preliminary #sqrt{s} = 8 TeV, #int L dt = %.1f fb^{-1}" % (float(lumi)/1000.0))
    text.SetShadowColor(ROOT.kWhite)
    text.SetLineColor(ROOT.kWhite)
    text.SetFillColor(ROOT.kWhite)
    text.Draw()
    return text

def merge_hists(hists_d, merge_groups):
    out_d = dict()
    for merge_name, items in merge_groups.items():
        hist = hists_d[items[0]].Clone()
        for item in items[1:]:
            hist.Add(hists_d[item])

        out_d[merge_name] = hist
        out_d[merge_name].SetTitle("%s" % merge_name)
    return out_d
