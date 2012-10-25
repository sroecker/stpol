import subprocess

def runJob(jobName, cfg, inf, ofdir=""):
    singleFile = not inf.endswith(".txt")

    if singleFile:
        if not inf.startswith("/store"):
            inf = "file:" + inf

    cfgName = cfg[cfg.rindex("/")+1:cfg.index(".py")]
    of = ofdir + "/" + jobName + cfgName +".root"
    logfn = ofdir + "/" + jobName + cfgName + ".log"
    if singleFile:
        inputCmd = "inputFiles=%s" % inf
    else:
        inputCmd = "inputFiles_load=%s" % inf

    p = subprocess.Popen("cmsRun %s %s outputFile=%s maxEvents=-1 &> %s &" % (cfg, inputCmd, of, logfn), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    print "Started job %s, logging to %s" % (jobName, logfn)
    return


Tbar_53X = "/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0077EE51-88DC-E111-88BE-0018F3D09684.root"
WJets_all = "fileLists/WJets.txt"
TTBar_all = "fileLists/TTBar.txt"
Tbar_t_all = "fileLists/TBar_t.txt"
Data_SingleMu_all = "fileLists/Data_SingleMu_RunA.txt"

#step2_cfg = "$CMSSW_BASE/src/SingleTopPolarization/Analysis/python/selection_step2_cfg.py"
step2_MC_cfg = "./step2_MC_cfg.py"
step2_Data_cfg = "./step2_Data_cfg.py"

runJob("sync_Tbar_53X", "./runconfs/step1_MC_cfg.py", Tbar_53X, ofdir="sync_step1")
#runJob("sync_Tbar_53X", "step1_noTauTrue_cfg.py", Tbar_53X, ofdir="sync_step1")
#runJob("sync_Tbar_53X", "step1_noSkim_cfg.py", Tbar_53X, ofdir="sync_step1")
#runJob("TTBar_", "step1_cfg.py", TTBar, "testRun_v1")
#runJob("WJets_", "step1_cfg.py", WJets, "testRun_v1")
#runJob("data1_", "step1_Data_cfg.py", data1, "testRun_v1")


#runJob("TTBar_", step2_cfg, TTBar_all, "testRun_v1")
#runJob("WJets_", step2_MC_cfg, WJets_all, "testRun_v1")
#runJob("Data_SingleMu2012A_", step2_Data_cfg, Data_SingleMu_all, "testRun_v1")

