from Cheetah.Template import Template
import json
effs = json.loads(open("bTaggingEffs.json").read())
temp = r"""
#compiler-settings
cheetahVarStartToken = @
#end compiler-settings
\begin{tabular}{ |c|c|c|c|c|c| }
     \hline
     MC sample & MC events in sel. & flavour & total & b-tagged & $\epsilon $\\
     \hline
     \multirow{3}{*}{single top, t-channel, top} & \multirow{3}{*}{@effs['T_t']['count_events']} & b & @effs['T_t']['count_b_total'] & @effs['T_t']['count_b_tagged'] & $ #echo '%.1f' % @effs['T_t']['eff_b']# \pm #echo '%.1f' % @effs['T_t']['sigma_eff_b']#\%$ \\\cline{3-6}
                                                 &                                               & c & @effs['T_t']['count_c_total'] & @effs['T_t']['count_c_tagged'] & $ #echo '%.2f' % @effs['T_t']['eff_c']# \pm #echo '%.2f' % @effs['T_t']['sigma_eff_c']#\%$ \\\cline{3-6}
                                                 &                                               & l & @effs['T_t']['count_l_total'] & @effs['T_t']['count_l_tagged'] & $ #echo '%.3f' % @effs['T_t']['eff_l']# \pm #echo '%.3f' % @effs['T_t']['sigma_eff_l']#\%$ \\\cline{3-6}
     \hline
     \multirow{3}{*}{$t\bar{t}$} & \multirow{3}{*}{@effs['TTbar']['count_events']} & b & @effs['TTbar']['count_b_total'] & @effs['TTbar']['count_b_tagged'] & $ #echo '%.1f' % @effs['TTbar']['eff_b']# \pm #echo '%.1f' % @effs['TTbar']['sigma_eff_b']#\%$ \\\cline{3-6}
                                      &                                            & c & @effs['TTbar']['count_c_total'] & @effs['TTbar']['count_c_tagged'] & $ #echo '%.2f' % @effs['TTbar']['eff_c']# \pm #echo '%.2f' % @effs['TTbar']['sigma_eff_c']#\%$ \\\cline{3-6}
                                      &                                            & l & @effs['TTbar']['count_l_total'] & @effs['TTbar']['count_l_tagged'] & $ #echo '%.3f' % @effs['TTbar']['eff_l']# \pm #echo '%.3f' % @effs['TTbar']['sigma_eff_l']#\%$ \\\cline{3-6}
     \hline
     \multirow{3}{*}{$W (\rightarrow l\nu) + jets $} & \multirow{3}{*}{@effs['WJets']['count_events']} & b & @effs['WJets']['count_b_total'] & @effs['WJets']['count_b_tagged'] & $ #echo '%.1f' % @effs['WJets']['eff_b']# \pm #echo '%.1f' % @effs['WJets']['sigma_eff_b']#\%$ \\\cline{3-6}
                             &                                                 & c & @effs['WJets']['count_c_total'] & @effs['WJets']['count_c_tagged'] & $ #echo '%.2f' % @effs['WJets']['eff_c']# \pm #echo '%.2f' % @effs['WJets']['sigma_eff_c']#\%$ \\\cline{3-6}
                             &                                                 & l & @effs['WJets']['count_l_total'] & @effs['WJets']['count_l_tagged'] & $ #echo '%.3f' % @effs['WJets']['eff_l']# \pm #echo '%.3f' % @effs['WJets']['sigma_eff_l']#\%$ \\\cline{3-6}
    \hline
\end{tabular}
"""

print Template(temp, searchList=[{"effs": effs}])