import FWCore.ParameterSet.Config as cms

demo = cms.EDProducer('BTagSystematicsWeightProducer',
    SFb=cms.string("x"),
    SFc=cms.string("x"),
    SFl=cms.string("x"),
    SFlErrXBins=cms.vdouble([0,10,20]),
    SFlErrYBins=cms.vdouble([5,8])
)
