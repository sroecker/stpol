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
TTBar = "/store/mc/Summer12_DR53X/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/001C868B-B2E1-E111-9BE3-003048D4DCD8.root"
WJets = "/store/mc/Summer12_DR53X/WJetsToLNu_TuneZ2Star_8TeV-madgraph-tarball/AODSIM/PU_S10_START53_V7A-v1/0001/FE206A01-E4D0-E111-B360-003048673FE6.root"
#runJob("sync_Tbar_53X", "step1_cfg.py", Tbar_53X, ofdir="sync_step1")
runJob("sync_Tbar_53X", "step1_noTauTrue_cfg.py", Tbar_53X, ofdir="sync_step1")
#runJob("sync_Tbar_53X", "step1_noSkim_cfg.py", Tbar_53X, ofdir="sync_step1")
#runJob("TTBar_", "step1_cfg.py", TTBar, "testRun_v1")
#runJob("WJets_", "step1_cfg.py", WJets, "testRun_v1")
