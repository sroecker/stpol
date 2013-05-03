merge_cmds = dict()
merge_cmds["single #mu"] = ["SingleMuAB", "SingleMuC", "SingleMuD"]
merge_cmds["diboson"] = ["WW", "WZ", "ZZ"]
merge_cmds["DY-jets"] = ["DYJets"]
merge_cmds["s-channel"] = ["T_s", "Tbar_s"]
merge_cmds["tW-channel"] = ["T_tW", "Tbar_tW"]
merge_cmds["t#bar{t}"] = ["TTJets_FullLept", "TTJets_SemiLept"]
merge_cmds["W(#rightarrow l #nu) + jets"] = ["W1Jets_exclusive", "W2Jets_exclusive", "W3Jets_exclusive", "W4Jets_exclusive"]

sample_names = dict()
for (name, items) in merge_cmds.items():
    for i in items:
        sample_names[i] = name