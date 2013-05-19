qcd_fitvalue = { # values returned by the theta-auto fit in different control regions without MET requirement
    "final_lep" :   2096,
    "final_incl":   1800,
    "2j1t_lep"  :   1,
    "2j1t_incl":    1,
    "2j0t_lep"  :   1,
    "2j0t_incl":    52240,
    }

qcd_template_size = { # the size of template in the control region (actually identical for inclusive and lepotnic samples (comes directly from data) )
    "final_lep" :  642,
    "final_incl":  642,
    "2j1t_lep"  :  47031,
    "2j1t_incl":   47031,
    "2j0t_lep":    16793,
    "2j0t_incl":   16793,
    }


def getQCDYield( qcd_temp_hist, mode = "final", doDebug = False ):
    qcd_yield = qcd_fitvalue[mode] * qcd_temp_hist.Integral()/qcd_template_size[mode]
    if doDebug:
        print "QCD yield from fit = " + str( qcd_fitvalue[mode] )
        print "Efficiency from control region to selected region = " + str( qcd_temp_hist.Integral()/qcd_template_size[mode] )
    return qcd_yield
