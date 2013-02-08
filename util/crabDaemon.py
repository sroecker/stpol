import re
import subprocess
import os
import sys
import datetime
import time
import signal
import glob
import pdb
import datetime

class CrabFailedException(Exception):
    pass

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class CrabStatus:
    def __init__(self):
        self.r = re.compile("^\d+\s*[YN].*$")

    @staticmethod
    def getStatusLines(lines):
        r = re.compile("^\d+\s*[YN].*$")
        lines = filter(lambda x: len(x)==1, map(r.findall, lines))
        lines = map(lambda x: x[0], lines)
        lines = map(lambda x: x.split(), lines)
        return lines

    @staticmethod
    def extCommand(cmd, fname, timeout=1200, retries=3, sleeptime=60):
        for i in range(retries):
            try:
                f = open(fname, "w")
                #print "Calling %s" % cmd
                p = subprocess.Popen(cmd, shell=True, stdout=f)
                start = datetime.datetime.now()
                while p.poll() is None:
                    time.sleep(1)
                    now = datetime.datetime.now()
                    if (now - start).seconds> timeout:
                        os.kill(p.pid, signal.SIGKILL)
                        os.waitpid(-1, os.WNOHANG)
                        raise CrabFailedException("Crab timed out")
                f.close()
                f = open(fname, "r")
                lines = f.readlines()
                f.close()
                if p.returncode == 0:
                    break
                else:
                    raise CrabFailedException("Crab process did not complete successfully: {0}".format(''.join(lines)))
            except CrabFailedException as e:
                print "Crab call '{1}' failed on try {0}".format(i, cmd)
                print "Sleeping {0} seconds before next try".format(sleeptime)
                time.sleep(sleeptime)
                if i+1 == retries:
                    raise e

        os.remove(fname)
        return lines

    @staticmethod
    def getStatus(d):
        outfile = d+".out"
        lines = CrabStatus.extCommand("crab -c %s -status" % d, outfile)
        statuslines = CrabStatus.getStatusLines(lines)
        statuses = [JobStatus(int(x[0]), x[2], x[3:]) for x in statuslines]
        return statuses

    @staticmethod
    def getResults(d):
        outfile = d+".out"
        lines = CrabStatus.extCommand("crab -c %s -get" % d, outfile)
        statusLines = re.findall("crab:  Results of Jobs # [0-9]+", ''.join(lines))
        gotJobs = map(lambda x: int(x[-1]), map(lambda x: x.split(), statusLines))
        return gotJobs

    @staticmethod
    def resubmit(d, statuses):
        idxList = JobStatus.indices(statuses)
        idxList = map(str, idxList)
        c = chunks(idxList, 100)
        for chunk in c:
            s = ",".join(chunk)
            try:
                out = CrabStatus.extCommand("crab -c %s -kill %s" % (d, s), "resub", retries=1, sleeptime=0)
                out = CrabStatus.extCommand("crab -c %s -get %s" % (d, s), "resub", retries=1, sleeptime=0)
            except CrabFailedException as e:
                print "Could not kill/get job to resubmit, probably no need to."
                pass
            out = CrabStatus.extCommand("crab -c %s -resubmit %s" % (d, s), "resub")
        return

    @staticmethod
    def submit(d, statuses):
        idxList = JobStatus.indices(statuses)
        idxList = map(str, idxList)
        c = chunks(idxList, 100)
        for chunk in c:
            s = ",".join(chunk)
            out = CrabStatus.extCommand("crab -c %s -submit %s" % (d, s), "sub")
        return

class JobStatus:
    def __init__(self, N, status, pars):
        self.N = N
        self.status = status
        self.pars = pars
        self.retcode = None
        if status == "Done" or status=="Retrieved":
            pars = pars[0:3]
            try:
                self.retcode = int(pars[2])
            except ValueError:
                self.retcode = None
            except IndexError:
                self.retcode = None
        elif status == "Cancelled":
            self.retcode = -1

    def __str__(self):
        if hasattr(self, "retcode"):
            return "%d: %s %s" % (self.N, self.status, str(self.retcode))
        else:
             return "%d: %s" % (self.N, self.status)

    def __repr__(self):
        return str(self)


    def requiresResub(self):
#        if self.N == 275:
#            pdb.set_trace()
        if self.status=="Aborted" \
            or self.status=="Done" and (self.retcode>0)\
            or self.status=="Retrieved" and (self.retcode>0)\
            or self.status=="Cancelled":
            print "DEBUG:requiresResub: {0}".format(self)
            return True
        else:
            return False

    @staticmethod
    def withStatus(statuses, s):
        return filter(lambda x: x.status == s, statuses)

    @staticmethod
    def indices(statuses):
        return sorted(map(lambda x: x.N, statuses))

    @staticmethod
    def statusTable(statuses):
        retrievedDict = {0: 0}
        outD = {}
        for s in statuses:
            if s.status == "Retrieved":
                if s.retcode not in retrievedDict.keys():
                    retrievedDict[s.retcode] = 0
                retrievedDict[s.retcode] += 1
            elif not s.status in outD.keys():
                outD[s.status] = 1
            else:
                outD[s.status] += 1
        outD["Retrieved"] = retrievedDict
        return outD

def jobLog(f, crabdir, jobIdx, command, status):
    fil = open(f, "a+")
    fil.write("{4} {0} {1} {2} {3}\n".format(crabdir, jobIdx, command, status, datetime.datetime.now()))
    fil.close()

def parseDir(d, resub, ofile):
    crabdir = d

    statuses = None

    #submit all created jobs
    while True:
        statuses = CrabStatus.getStatus(crabdir)
        jobsToSub = filter(lambda x: x.status=="Created", statuses)
        if len(jobsToSub)==0:
            break
        print "Submitting {0} jobs: {1}".format(len(jobsToSub), JobStatus.indices(jobsToSub))
        CrabStatus.submit(crabdir, jobsToSub)

    #Get all jobs
    jobsNotGot = []
    while True:
        statuses = CrabStatus.getStatus(d)
        jobsToGet = filter(lambda x: x.status=="Done" and x.retcode is None, statuses)
        if len(jobsToGet)>0:
            print "Getting {0} jobs: {1}".format(len(jobsToGet), JobStatus.indices(jobsToGet))
            gotJobIDs = CrabStatus.getResults(d)
        else:
            break
        if len(jobsToGet)!=len(gotJobIDs) or sum(map(lambda x: x[0]!=x[1].N, zip(gotJobIDs, jobsToGet)))>0:
            couldNotGet = list(set(JobStatus.indices(jobsToGet)).difference(set(gotJobIDs)))
            print "Problem getting jobs: {0}".format(couldNotGet)
            print "Resubmitting by force: {0}".format(couldNotGet)
            if resub:
                CrabStatus.extCommand("crab -c {0} -forceResubmit {1}".format(crabdir, ','.join(map(str, couldNotGet)) ), "resub")
                for j in couldNotGet:
                    jobLog(ofile, crabdir, j, "forceResubmit", "COULDNOTGET")

        statuses = CrabStatus.getStatus(d)
        jobsToResub = filter(lambda x: x.requiresResub(), statuses)
        if len(jobsToResub)==0:
            break
        print "Resubmitting {0} jobs: {1}".format(len(jobsToResub), JobStatus.indices(jobsToResub))
        retCodes = [x.retcode for x in jobsToResub]
        orderByFreq = list(set([(x, retCodes.count(x)) for x in retCodes]))
        orderByFreq.sort(key=lambda x: x[1], reverse=True)

        print "Most commot return codes: {0}".format(orderByFreq)
        try:
            CrabStatus.resubmit(crabdir, jobsToResub)
            for j in jobsToResub:
                jobLog(ofile, crabdir, j.N, "resubmit", j.retcode)
        except CrabFailedException as e:
            print "Could not resubmit with crab: {0}".format(e.message)

        statuses = CrabStatus.getStatus(d)

    statusTable = JobStatus.statusTable(statuses)
    print "Status total of {0} jobs: {1} | {2:.0%} done".format(len(statuses), JobStatus.statusTable(statuses), float(statusTable["Retrieved"][0])/float(len(statuses)))
    if len(statuses)==statusTable["Retrieved"][0]:
        print "Job {0} is done!".format(crabdir)

    return len(statuses)==statusTable["Retrieved"][0]

def signal_handler(signal, frame):
    print "SIGINT caught, exiting"
    sys.exit(0)


if __name__=="__main__":
    signal.signal(signal.SIGINT, signal_handler)
    incompleteJobs = []
    completeJobs = []
    ofile = "/home/joosep/web/crabOut.txt"

    try:
        while True:
            jobFile = open("jobList.txt", "r")
            incompleteJobs = jobFile.readlines()
            jobFile.close()
            incompleteJobs = map(lambda x: x.strip(), incompleteJobs)
            incompleteJobs = filter(lambda x: not x.startswith("!"), incompleteJobs)
            incompleteJobs = filter(lambda x: os.path.exists("{0}/share/crab.cfg".format(x)), incompleteJobs)
            incompleteJobs = list(set(incompleteJobs).difference(completeJobs))
            incompleteJobs.sort()
            jobFile = open("jobList.txt", "w+")
            for job in incompleteJobs:
                jobFile.write(job + "\n")
            for job in completeJobs:
                jobFile.write("!" + job + "\n")
            jobFile.close()
            print "Considering dirs: {0}".format(incompleteJobs)

            for d in incompleteJobs:
                print "{0}".format(str(datetime.datetime.now().__str__()))
                print "***Checking %s***" % d
                isDone = parseDir(d, "resub" in sys.argv, ofile)
                if isDone:
                    completeJobs.append(d)
            if len(incompleteJobs)==0:
                print "All jobs are completed, exiting"
                sys.exit(1)
            print 80*"-"
    except KeyboardInterrupt:
        print "CTRL-C caught, exiting"
        sys.exit(0)
