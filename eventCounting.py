import FWCore.ParameterSet.Config as cms

def countInSequence(process, path):
  pathName = path.label()
  preCountName = pathName + "PreCount"
  postCountName = pathName + "PostCount"
  setattr(process, preCountName, cms.EDProducer("EventCountProducer"))
  setattr(process, postCountName, cms.EDProducer("EventCountProducer"))

  path.insert(0, getattr(process, preCountName))
  path.insert(-1, getattr(process, postCountName))
