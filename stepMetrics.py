#!/usr/bin/python

#This program analyzes the efficiency of a CMSSW analysis step and calculates the metrics for a grid job configuration

import subprocess
import sys
import os

inputRootFile = sys.argv[1]
inputSTDOUTFile = sys.argv[2]

def call(cmd, retError=False):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = p.communicate()
    if retError:
        return output, errors
    else:
        return output

effCalc = "SingleTopPolarization/EfficiencyAnalyzer/efficiencyanalyzer_cfg.py"
effOut = call("cmsRun %s" % effCalc, retError=True)
eventsProcessed = long(effOut[0].split()[2])
eventTime = float(call("grep 'Real/event' %s" % inputSTDOUTFile).split()[-1])
temp = call("edmFileUtil '%s'" % inputRootFile).split()
fileSize = long(temp[-2])
eventsInFile = long(temp[-4])

eventSize = float(fileSize)/float(eventsInFile)
print "Event size after slimming: %d b/event" % eventSize
efficiency = 100.0*float(eventsInFile)/float(eventsProcessed)
print "Process efficiency: %.2f%% pass this step" % efficiency
eventsPerHour = 3600.0/eventTime
print "This step processes %d events/hour" % eventsPerHour
