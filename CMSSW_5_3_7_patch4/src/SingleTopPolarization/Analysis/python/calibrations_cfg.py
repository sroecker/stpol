import logging
import fnmatch
bTaggingEfficiencies = dict()

class BTaggingEfficiency:
    def __init__(self, eff_b, eff_c, eff_l):
        self.eff_b = eff_b
        self.eff_c = eff_c
        self.eff_l = eff_l
    def __str__(self):
        return str(self.__dict__)

BTaggingEfficiency.default = BTaggingEfficiency(0.0, 0.0, 0.0)

eff_ex_WJets_inclusive_2J =  {
    'b': (1.747E-01, 0.0),
    'c': (2.779E-02, 0.0),
    'l': (7.052E-04, 0.0)
}

eff_ex_WJets_inclusive_3J =  {
    'b': (1.923E-01, 0.0),
    'c': (3.654E-02, 0.0),
    'l': (7.123E-04, 0.0)
}

eff_ex_T_t_2J =  {
    'b': (4.338E-01, 0.0),
    'c': (3.750E-03, 0.0),
    'l': (1.967E-04, 0.0)
}

eff_ex_T_t_3J =  {
    'b': (4.276E-01, 0.0),
    'c': (6.601E-03, 0.0),
    'l': (7.610E-04, 0.0)
}

eff_ex_TTbar_inclusive_2J =  {
    'b': (2.957E-01, 0.0),
    'c': (2.443E-02, 0.0),
    'l': (6.127E-04, 0.0)
}

eff_ex_TTbar_inclusive_3J =  {
    'b': (3.815E-01, 0.0),
    'c': (2.466E-02, 0.0),
    'l': (9.813E-04, 0.0)
}


def setEffs(eff_ex_T_t, eff_ex_TTbar, eff_ex_WJets):
    effs = dict()

    b_T_t = eff_ex_T_t["b"][0]
    c_WJets = eff_ex_WJets["c"][0]
    l_T_t = eff_ex_T_t["l"][0]
    l_WJets=eff_ex_WJets["l"][0]
    l_TTbar = eff_ex_TTbar["l"][0]

    effs["T_t"] = BTaggingEfficiency(b_T_t, c_WJets, l_T_t)
    effs["Tbar_t"] = BTaggingEfficiency(b_T_t, c_WJets, l_T_t)
    effs["QCD*"] = BTaggingEfficiency.default
    effs["WJets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W1Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W2Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W3Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["W4Jets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["WW"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["WZ"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["ZZ"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["DYJets"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)
    effs["GJets*"] = BTaggingEfficiency(b_T_t, c_WJets, l_WJets)

    effs["TTbar"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["T_tW"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["T_s"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["Tbar_tW"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    effs["Tbar_s"] = BTaggingEfficiency(b_T_t, c_WJets, l_TTbar)
    return effs


bTaggingEfficiencies = dict()
bTaggingEfficiencies[2] = setEffs(eff_ex_T_t_2J, eff_ex_TTbar_inclusive_2J, eff_ex_WJets_inclusive_2J)
bTaggingEfficiencies[3] = setEffs(eff_ex_T_t_3J, eff_ex_TTbar_inclusive_3J, eff_ex_WJets_inclusive_3J)

def getEfficiencies(nJets, sample):
    logging.debug("Looking for efficiencies %s" % sample)
    eff = bTaggingEfficiencies[nJets]
    key = None
    for key in eff.keys():
        if fnmatch.fnmatch(sample, key):
            break
    if key is None:
        raise Exception("B-tagging efficiencies not defined for sample %s" % sample)
    logging.info("Matched efficiencies for key %s: %s" % (key, eff[key]))
    return eff[key]
