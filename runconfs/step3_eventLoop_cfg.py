from runconfs.step3_eventloop_base_nocuts import *

if options.lepton=="mu":
    process.muonCuts.cutOnIso = True
    process.muonCuts.requireOneMuon = True
    if options.doHLT:
        process.HLTMu.doCutOnHLT = True
elif options.lepton=="ele":
    process.electronCuts.cutOnIso = True
    process.electronCuts.requireOneElectron = True
    if options.doHLT:
        process.HLTEle.doCutOnHLT = True

