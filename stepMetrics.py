#!/usr/bin/python

#This program analyzes the efficiency of a CMSSW analysis step and calculates the metrics for a grid job configuration

import subprocess
import sys

stepCfgFile = "selection_step1_cfg.py"
inputRootFile = sys.argv[1]
tempROOTFile = "patTuple.root"
tempSTDOUT = "tempOut.STDOUT"
maxEvents = 100

def call(cmd, retError=False):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, errors = p.communicate()
    if retError:
        return output, errors
    else:
        return output

print "Calling cmsRun %s" % stepCfgFile
call("cmsRun %s inputFiles=%s maxEvents=%d outputFile=%s &> %s" % (stepCfgFile, inputRootFile, maxEvents, tempROOTFile, tempSTDOUT))

effCalc = "SingleTopPolarization/EfficiencyAnalyzer/efficiencyanalyzer_cfg.py"
print "Calling cmsRun %s" % effCalc
effOut = call("cmsRun %s" % effCalc, retError=True)
fileUtilOut = call("edmFileUtil %s" % tempROOTFile)

eventsProcessed = long(fileUtilOut.split()[-4])
eventTime = float(call("grep 'Real/event' %s" % tempSTDOUT).split()[-1])
temp = call("edmFileUtil '%s'" % inputRootFile).split()
fileSize = long(temp[-2])
eventsInFile = long(temp[-4])

eventSize = float(fileSize)/float(eventsInFile)
print "Event size after slimming: %d b/event" % eventSize
efficiency = 100.0*float(eventsInFile)/float(eventsProcessed)
print "Process efficiency: %.2f%% pass this step" % efficiency
eventsPerHour = 3600.0/eventTime
print "This step processes %d events/hour" % eventsPerHour
