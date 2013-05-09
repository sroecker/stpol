
hist_def = {
    "met": ["met", (100, 0, 200)],
    "top_mass": ["top_mass", (100, 50, 300)],
    "eta_lj": ["eta_lj", (100, 0, 5.0)],
    "pt_lj": ["pt_lj",(100, 0, 200)],
    "cos_theta": ["cos_theta", (100, -1.01, 1.01)],
    "el_pt": ["el_pt",(100, 20, 200)],
#    "el_mva": ["el_mva",(20, 0.8, 1.01)]
    }

sel_2j0t = "n_ele == 1 & n_jets == 2 & n_tags == 0"
sel_2j1t = "n_ele == 1 & n_jets == 2 & n_tags == 1 "
sel_3j1t = "n_ele == 1 & n_jets == 3 & n_tags == 1"
sel_3j2t = "n_ele == 1 & n_jets == 3 & n_tags == 2"

sel_ele = "el_mva > 0.9 & el_pt > 30"
sel_ele_antiiso = "el_pt > 30"

muon_veto = "n_muons == 0"

trigger = "( (HLT_Ele27_WP80_v10 ==1) || (HLT_Ele27_WP80_v11 == 1) || (HLT_Ele27_WP80_v9==1) || (HLT_Ele27_WP80_v8==1) )"

sel_met = "met > 45"
sel_topm = "top_mass > 130 & top_mass < 220"
sel_eta = "abs(eta_lj) > 2.5" 

cuts = {
    "2j0t_nomet": "(" + sel_2j0t + "&" + muon_veto + "&" + trigger + "&" + sel_ele + "&" + sel_topm + "&" + sel_eta  +")",
    "2j0t_nomet_antiiso": "(" + sel_2j0t + "&" + muon_veto + "&" + trigger + "&" + sel_topm + "&" + sel_eta  + ")",
    
    "2j0t": "(" + sel_2j0t + "&" + sel_met + ")",

    "2j1t_nomet": "(" + sel_2j1t + "&" + muon_veto + "&" + trigger + "&" + sel_ele + "&" + sel_topm + "&" + sel_eta  + ")",
    "2j1t_nomet_antiiso": "(" + sel_2j1t + "&" + muon_veto + "&" + trigger + "&" + sel_topm + "&" + sel_eta  + ")",

    "2j1t": "(" + sel_2j1t + "&" + sel_met + "&" + muon_veto + "&" + trigger + ")",

    "3j1t": "(" + sel_3j1t + "&" + sel_met + ")",
    "3j2t": "(" + sel_3j2t + "&" + sel_met + ")",

    "final": "(" + sel_2j1t + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + "&" + muon_veto  + "&" + trigger + "&" + sel_ele + ")",
    "final_antiiso": "(" + sel_2j1t + "&" + sel_met + "&" + sel_topm + "&" + sel_eta + "&" + muon_veto  + "&" + trigger +  ")"
    
    }
