import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.MessageLogger = cms.Service("MessageLogger",
       destinations   = cms.untracked.vstring(
                                              'cout',
                    ),
       debugModules   = cms.untracked.vstring('myProducerLabel'),
       cout       = cms.untracked.PSet(
                       threshold = cms.untracked.string('DEBUG')
        ),
)

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:output.root'
    )
)

SFb = "0.726981*((1.+(0.253238*x))/(1.+(0.188389*x)))"
SFc = SFb
SFbErrBinsY = [0.0554504,
         0.0209663,
         0.0207019,
         0.0230073,
         0.0208719,
         0.0200453,
         0.0264232,
         0.0240102,
         0.0229375,
         0.0184615,
         0.0216242,
         0.0248119,
         0.0465748,
         0.0474666,
         0.0718173,
         0.0717567]
SFbErrBinsX = [20, 30, 40, 50, 60, 70, 80, 100, 120, 160, 210, 260, 320, 400, 500, 600, 800]
SFcErrBinsY = 2 * SFbErrBinsY
SFcErrBinsX = SFbErrBinsX

process.myProducerLabel = cms.EDProducer('BTagSystematicsWeightProducer',
    src=cms.InputTag("goodJets"),

    nJets=cms.uint32(3),
    nTags=cms.uint32(2),

    SFb=cms.string(SFb),
    SFc=cms.string(SFc),
    SFl=cms.string("x"),

    SFlErrBinsX=cms.vdouble([10,20]),
    SFlErrBinsY=cms.vdouble([10]),

    SFbErrBinsX=cms.vdouble(SFbErrBinsX),
    SFbErrBinsY=cms.vdouble(SFbErrBinsY),

    SFcErrBinsX=cms.vdouble(SFbErrBinsX),
    SFcErrBinsY=cms.vdouble(SFbErrBinsY),

    Effb=cms.double(0.9),
    Effc=cms.double(0.1),
    Effl=cms.double(0.1)
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)


process.p = cms.Path(process.myProducerLabel)

process.e = cms.EndPath(process.out)
