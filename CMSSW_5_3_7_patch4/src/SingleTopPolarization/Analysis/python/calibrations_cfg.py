bTaggingEfficiencies = dict()

class BTaggingEfficiency:
    def __init__(self, eff_b, eff_c, eff_l):
        self.eff_b = eff_b
        self.eff_c = eff_c
        self.eff_l = eff_l
    def __str__(self):
        return str(self.__dict__)

BTaggingEfficiency.default = BTaggingEfficiency(0.0, 0.0, 0.0)

eff_ex_WJets = {
    "eff_b": 2.04E-01,
    "eff_c": 2.91E-02,
    "eff_l": 7.66E-04
}

eff_ex_T_t = {
    "eff_b": 4.31E-01,
    "eff_c": 8.39E-03,
    "eff_l": 1.22E-04,
}

eff_ex_TTbar = {
    "eff_b": 3.97E-01,
    "eff_c": 3.21E-02,
    "eff_l": 1.11E-03,
}


bTaggingEfficiencies["T_t"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_T_t["eff_l"])
bTaggingEfficiencies["Tbar_t"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_T_t["eff_l"])

bTaggingEfficiencies["WJets"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["WW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["WZ"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["ZZ"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])
bTaggingEfficiencies["DYJets"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_WJets["eff_l"])

bTaggingEfficiencies["TTbar"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["T_tW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["T_s"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["Tbar_tW"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
bTaggingEfficiencies["Tbar_s"] = BTaggingEfficiency(eff_ex_T_t["eff_b"], eff_ex_WJets["eff_c"], eff_ex_TTbar["eff_l"])
