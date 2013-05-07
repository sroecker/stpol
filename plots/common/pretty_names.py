from utils import merge_cmds

sample_names = dict()
for (name, items) in merge_cmds.items():
    for i in items:
        sample_names[i] = name

variable_names = dict()
variable_names["eta_lj"] = "#eta_{lj}"
variable_names["abs_eta_lj"] = "|#eta_{lj}|"
variable_names["top_mass"] = "m(l #nu j)"
variable_names["cos_theta"] = "cos#theta*"
variable_names["met"] = "MET"
variable_names["el_pt"] = "lepton p_{T}"

variable_units = dict()
variable_units["eta_lj"] = ""
variable_units["abs_eta_lj"] = ""


