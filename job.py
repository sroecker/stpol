import subprocess

def runJob(jobName, cfg, inf, ofdir=""):
    if not inf.startswith("/store"):
        inf = "file:" + inf
    cfgName = cfg[:cfg.index(".py")]
    of = ofdir + "/" + jobName + cfgName +".root"
    logfn = ofdir + "/" + jobName + cfgName + ".log"

    p = subprocess.Popen("cmsRun %s inputFiles=%s outputFile=%s maxEvents=-1 &> %s &" % (cfg, inf, of, logfn), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (out, err) = p.communicate()
    print "Started job %s, logging to %s" % (jobName, logfn)
    return


Tbar_53X = "/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0077EE51-88DC-E111-88BE-0018F3D09684.root"


runJob("sync_Tbar_53X", "step1_cfg.py", Tbar_53X, ofdir="sync_step1")
runJob("sync_Tbar_53X", "step1_noSkim_cfg.py", Tbar_53X, ofdir="sync_step1")
