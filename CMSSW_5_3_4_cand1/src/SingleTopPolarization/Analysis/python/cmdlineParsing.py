from FWCore.ParameterSet.VarParsing import VarParsing
import FWCore.ParameterSet.Config as cms

def enableCommandLineArguments(process):
    options = VarParsing('analysis')
    options.parseArguments()
    process.source.fileNames = cms.untracked.vstring(options.inputFiles)
    process.maxEvents = cms.untracked.PSet(
      input = cms.untracked.int32(options.maxEvents)
    )
    process.out.fileName = cms.untracked.string(options.outputFile)
