import subprocess

def runJob(jobName, inf, ofdir):
	if not inf.startswith("/store"):
		inf = "file:" + inf
	of = ofdir + "/" + jobName + ".root"
	logfn = ofdir + "/" + jobName + ".log"

	p = subprocess.Popen("cmsRun step1_cfg.py inputFiles=%s outputFile=%s maxEvents=-1 &> %s &" % (inf, of, logfn), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	(out, err) = p.communicate()
	print "Started job %s, logging to %s" % (jobName, logfn)
	return


Tbar_53X = "/store/mc/Summer12_DR53X/T_t-channel_TuneZ2star_8TeV-powheg-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/0077EE51-88DC-E111-88BE-0018F3D09684.root"


runJob("sync_Tbar_53X_step1", Tbar_53X, "sync_step1")