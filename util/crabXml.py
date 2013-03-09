from xml.dom.minidom import parse
import numpy
from collections import OrderedDict as dict
import time
import datetime

class Task:
	def __init__(self):
		self.prev_jobs = []
		self.jobs = []
		self.name = None

	@staticmethod
	def parseJob(args):
		job, running_job = args
		id = get(job, "jobId", int)
		name = get(job, "name", str)
		submission = get(running_job, "submission", int)
		schedulerId = get(running_job, "schedulerId", int)
		submissionTime = get(running_job, "submissionTime", str)
		getOutputTime = get(running_job, "getOutputTime", str)
		wrapperReturnCode = get(running_job, "wrapperReturnCode", int)
		applicationReturnCode = get(running_job, "applicationReturnCode", int)
		state = get(running_job, "state", str)
		return Job(name, id, submission, schedulerId, submissionTime, getOutputTime, applicationReturnCode, wrapperReturnCode, state)


	def updateJobs(self, fname):
		dom = parse(fname)
		jobs_a = dom.getElementsByTagName("Job")
		jobs_b = dom.getElementsByTagName("RunningJob")
		self.prev_jobs = self.jobs
		self.jobs = map(Task.parseJob, zip(jobs_a, jobs_b))
		self.name = self.jobs[0].name

	@staticmethod
	def timeStats(jobs):
		times = map(
			lambda j: j.totalTime().seconds,
			jobs
		)
		median_time = datetime.timedelta(seconds=int(numpy.median(times)))
		mean_time = datetime.timedelta(seconds=int(numpy.mean(times)))
		min_time = datetime.timedelta(seconds=int(numpy.min(times)))
		max_time = datetime.timedelta(seconds=int(numpy.max(times)))
		return mean_time, median_time, min_time, max_time

	def getStats(self):
		completed = filter(lambda j: j.isCompleted(), self.jobs)
		needs_get = filter(lambda j: j.needsGet(), self.jobs)
		median_submissions = int(numpy.median(map(lambda j: j.n_submission, self.jobs)))
		 
		max_submissions = numpy.max(map(lambda j: j.n_submission, self.jobs))
		needs_resubmit = filter(lambda j: j.needsResubmit(), self.jobs)
		r = dict()

		r["N_total"] = len(self.jobs)
		r["N_completed"] = len(completed)
		r["N_needs_get"] = len(needs_get)
		r["N_needs_resubmit"] = len(needs_resubmit)
		r["median_submissions"] = median_submissions
		r["max_submissions"] = max_submissions
		r["median_time_success"], r["mean_time_success"], r["min_time_success"], r["max_time_success"] = Task.timeStats(filter(lambda x: x.isCompleted(), self.jobs))
		r["median_time_fail"], r["mean_time_fail"], r["min_time_fail"], r["max_time_fail"] = Task.timeStats(filter(lambda x: x.needsResubmit(), self.jobs))
		r["fail_codes"] = Task.retCodes(filter(lambda x: x.needsResubmit(), self.jobs))
		return r

	@staticmethod
	def retCodes(jobs):
		rets = dict()
		for j in jobs:
			if (j.wrapper_ret_code, j.app_ret_code) not in rets.keys():
				rets[(j.wrapper_ret_code, j.app_ret_code)] = 0
			rets[(j.wrapper_ret_code, j.app_ret_code)] += 1
		return rets

	def printStats(self):
		stats = self.getStats()
		ret = self.name + "\n"
		for (k, v) in stats.items():
			ret += "%s: %s\n" % (k, v)
		return ret

def maketime(s):
	return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, "%Y-%d-%m %H:%M:%S")))
class Job:
	def __init__(self,
		name,
		job_id,
		n_submission,
		scheduler_id,
		submission_time,
		get_output_time,
		wrapper_ret_code,
		app_ret_code,
		state
	):
		self.name = name
		self.job_id = job_id
		self.n_submission = n_submission
		self.scheduler_id = scheduler_id
		self.submission_time = maketime(submission_time)
		self.get_output_time = maketime(get_output_time) if get_output_time is not None else None
		self.wrapper_ret_code = wrapper_ret_code if wrapper_ret_code is not None else -1
		self.app_ret_code = app_ret_code if app_ret_code is not None else -1
		self.state = state

	def isCompleted(self):
		return self.state == "Cleared" and self.wrapper_ret_code == 0 and self.app_ret_code == 0

	def needsGet(self):
		return self.state == "Terminated"

	def needsResubmit(self):
		return self.state == "Cleared" and not self.isCompleted()

	def totalTime(self):
		t1 = self.get_output_time if self.get_output_time is not None else time.localtime()
		return t1 - self.submission_time

	def __repr__(self):
		return "Job(%d,%d): %s %d %d %s %s" % (
			self.job_id,
			self.scheduler_id,
			self.state, 
			self.app_ret_code,
			self.wrapper_ret_code,
			self.submission_time,
			self.get_output_time
		)

def get(node, name, f):
	val = node.attributes.getNamedItem(name)
	if val is None:
		return None
	else:
		return f(val.nodeValue)


t = Task()
t.updateJobs("RReport.xml")