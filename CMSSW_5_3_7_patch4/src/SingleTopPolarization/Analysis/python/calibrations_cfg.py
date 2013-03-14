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

eff_ex_WJets_inclusive_2J =  {'c': (0.033669202553330141, 8.7078623740220199e-07), 'b': (0.15474389704684555, 3.0626084247596172e-06), 'l': (0.00077350221843158252, 3.796120390908692e-07)}
eff_ex_WJets_inclusive_3J =  {'c': (0.047166694074271022, 1.6712552340373514e-06), 'b': (0.23400361829108529, 3.8975395369241771e-06), 'l': (0.00073873536881525765, 8.2955693648926585e-07)}
eff_ex_T_t_2J =  {'c': (0.0025906670144525286, 1.5520465333569895e-06), 'b': (0.44922469476074101, 2.3290812525022726e-07), 'l': (0.0, -1)}
eff_ex_T_t_3J =  {'c': (0.0075754770773320693, 2.647378053639123e-06), 'b': (0.58066222522631761, 4.4443449005479932e-07), 'l': (0.00063202787347951112, 7.6734921984703091e-07)}
eff_ex_TTbar_inclusive_2J =  {'c': (0.027368308408464645, 1.381620396746298e-06), 'b': (0.37158178724055058, 4.4833184660839811e-07), 'l': (0.0010192517018663863, 6.8891637980829315e-07)}
eff_ex_TTbar_inclusive_3J =  {'c': (0.026405055702652745, 8.7925344497782043e-07), 'b': (0.48746501312608759, 3.2499313136967755e-07), 'l': (0.0010913820425246931, 5.0406148279971367e-07)}


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
    eff = bTaggingEfficiencies[nJets]
    key = None
    for key in eff.keys():
        if fnmatch.fnmatch(sample, key):
            break
    if key is None:
        raise Exception("B-tagging efficiencies not defined for sample %s" % sample)
    logging.info("Matched efficiencies for key %s: %s" % (key, eff[key]))
    return eff[key]
