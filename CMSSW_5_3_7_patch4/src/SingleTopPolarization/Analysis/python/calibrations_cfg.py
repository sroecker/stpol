bTaggingEfficiencies = dict()

class BTaggingEfficiency:
    def __init__(self, eff_b, eff_c, eff_l):
        self.eff_b = eff_b
        self.eff_c = eff_c
        self.eff_l = eff_l
    def __str__(self):
        return str(self.__dict__)

eff_ex_WJets = {"eff_b": 0.9545454545454546, "eff_c": 1.0, "eff_l": 0.12307692307692308}
eff_ex_T_t = {"eff_b": 0.9869394862864606, "eff_c": 0.0, "eff_l": 0.00019790223629527012}
eff_ex_TTbar = {"eff_b": 0.7639405204460966, "eff_c": 0.09345794392523364, "eff_l": 0.0027472527472527475}


bTaggingEfficiencies["T_t"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_T_t["eff_l"])
bTaggingEfficiencies["Tbar_t"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_T_t["eff_l"])

bTaggingEfficiencies["WJets"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["WW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["WZ"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["ZZ"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])

bTaggingEfficiencies["TTbar"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["T_tW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["T_s"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["Tbar_tW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["Tbar_s"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
