from Fit import Fit

triggers="(HLT_IsoMu24_eta2p1_v11==1 || HLT_IsoMu24_eta2p1_v12==1 || HLT_IsoMu24_eta2p1_v13==1 || HLT_IsoMu24_eta2p1_v14==1 || HLT_IsoMu24_eta2p1_v15==1 || HLT_IsoMu24_eta2p1_v16==1 || HLT_IsoMu24_eta2p1_v17==1)"
weightsQCD = triggers+"*pu_weight"#*muon_IDWeight*muon_IsoWeight"
weightsMC = weightsQCD# + "*b_weight_nominal"
weightsData = triggers

base_cuts = "pt_lj>40 && pt_bj>40"
base_cuts += " && abs(eta_lj)>2.5" 

cutsSR = "(top_mass < 220 && top_mass > 130)"
cutsSB = "(top_mass > 220 || top_mass < 130)"

def get_jet_cuts(fit, isQCD=False):
   if isQCD and fit.isMC:
      jet_cuts = " && n_jets == %i && n_tags == 0" % (fit.jets)
   else:
      jet_cuts = " && n_jets == %i && n_tags == %i" % (fit.jets, fit.tags)
      jet_cuts += " && rms_lj<0.025"
   return jet_cuts

def get_cuts_iso(fit):
   iso_cuts = base_cuts + " && mu_iso<0.12"
   iso_cuts += " && " + get_mtw_cut(fit)
   if fit.isSR:
      iso_cuts += " && "+cutsSR
   elif fit.isSB:
      iso_cuts += " && "+cutsSB
   iso_cuts += get_jet_cuts(fit)
   return iso_cuts

def get_weights():
   return 


def get_isolation_cut(iso_var, fit=Fit()):
   if fit.extra == "iso_0_3_plus":
      if iso_var=="iso_plus":
         return "(mu_iso > 0.33 && mu_iso < 0.99)"
      elif iso_var=="iso_minus":
         return "(mu_iso > 0.3 && mu_iso < 0.9)"
      else:
         return "(mu_iso > 0.27 && mu_iso < 0.81)"
   elif fit.extra == "iso_0_5_plus":
      if iso_var=="iso_plus":
         return "(mu_iso > 0.55 && mu_iso < 0.99)"
      elif iso_var=="iso_minus":
         return "(mu_iso > 0.45 && mu_iso < 0.81)"
      else:
         return "(mu_iso > 0.5 && mu_iso < 0.9)"
   else:
      if iso_var=="iso_plus":
         return "(mu_iso > 0.33 && mu_iso < 0.55)"
      elif iso_var=="iso_minus":
         return "(mu_iso > 0.27 && mu_iso < 0.45)"
      else:
         return "(mu_iso > 0.3 && mu_iso < 0.5)"

def get_mtw_cut(fit):
   if fit.extra == "mtwMass20plus":
      return "mt_mu>20"
   elif fit.extra == "mtwMass50":
      return "mt_mu<50"
   elif fit.extra == "mtwMass70":
      return "mt_mu<70"
   else:
      return "1"

def get_cuts_iso_data(fit):
   return weightsData+"*("+get_cuts_iso(fit)+")"

def get_cuts_iso_mc(fit):
   #print weightsMC+"*("+get_cuts_iso(fit)+")"
   return weightsMC+"*("+get_cuts_iso(fit)+")"
   

def get_cuts_antiiso_data(fit, iso_var=""):
   return weightsData+"*("+get_cuts_antiiso(fit, iso_var)+")"

def get_cuts_antiiso_data_fitted(fit, iso_var=""):
   return weightsData+"*(mt_mu>50 && "+get_cuts_antiiso(fit, iso_var)+")"

def get_cuts_antiiso_mc(fit, iso_var=""):
   return weightsMC+"*("+get_cuts_antiiso(fit, iso_var)+")"

def get_cuts_antiiso(fit, iso_var="", isQCD=False):
   antiiso_cuts = base_cuts +" && (deltaR_lj > 0.3 && deltaR_bj > 0.3) && " +get_isolation_cut(iso_var, fit)
   antiiso_cuts += " && " + get_mtw_cut(fit)
   if fit.isSR:
      antiiso_cuts += " && "+cutsSR
   elif fit.isSB:
      antiiso_cuts += " && "+cutsSR
   antiiso_cuts += get_jet_cuts(fit, isQCD)
   return antiiso_cuts
   
def get_cuts_antiiso_qcd(fit, iso_var=""):
   return weightsQCD+"*("+get_cuts_antiiso(fit, iso_var, isQCD=True)+")"

##################

def get_cuts_iso_data_manual(cuts, n_jets, n_tags):
   return weightsData+"*("+get_cuts_iso_manual(cuts, n_jets, n_tags)+")"

def get_cuts_iso_mc_manual(cuts, n_jets, n_tags):
   return weightsMC+"*("+get_cuts_iso_manual(cuts, n_jets, n_tags)+")"

def get_cuts_iso_manual(cuts, n_jets, n_tags):
   iso_cuts = cuts + " && mu_iso<0.12"
   iso_cuts += get_jet_cuts_manual(n_jets, n_tags)
   return iso_cuts

def get_jet_cuts_manual(n_jets, n_tags):
   jet_cuts = " && n_jets == %i && n_tags == %i" % (n_jets, n_tags)
   return jet_cuts

###

def get_cuts_antiiso_data_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var=""):
   return weightsData+"*("+get_cuts_antiiso_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var)+")"

def get_cuts_antiiso_mc_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var=""):
   return weightsMC+"*("+get_cuts_antiiso_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var)+")"

def get_cuts_antiiso_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var=""):
   antiiso_cuts = cuts + " && " + anti_iso_cuts + " && " + get_isolation_cut(iso_var)
   antiiso_cuts += get_jet_cuts_manual(n_jets, n_tags)
   return antiiso_cuts
   
def get_cuts_antiiso_qcd_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var=""):
   return weightsQCD+"*("+get_cuts_antiiso_manual(cuts, anti_iso_cuts, n_jets, n_tags, iso_var)+")"











