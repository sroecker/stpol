qcd_fitvalue = { # values returned by the theta-auto fit in different control regions without MET requirement
    "final_lep" :   1343,
    "final_incl":   1129,
    "2j1t_lep"  :   16848,
    "2j1t_incl":    16217,
    "2j0t"  :       38990,
    }

qcd_template_size = { # the size of template in the control region (actually identical for inclusive and lepotnic samples (comes directly from data) )
    "final_lep" :  1808,
    "final_incl":  1808,
    "2j1t_lep"  :  47031,
    "2j1t_incl":   47031,
    "2j0t":        1, #FIXME
    }


def getQCDYield( qcd_temp_hist, mode = "final", doDebug = False ):
    qcd_yield = qcd_fitvalue[mode] * qcd_temp_hist.Integral()/qcd_template_size[mode]
    if doDebug:
        print "QCD yield from fit = " + str( qcd_fitvalue[mode] )
        print "Efficiency from control region to selected region = " + str( qcd_temp_hist.Integral()/qcd_template_size[mode] )
    return qcd_yield
