import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST3")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/jpata/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/stpol_Feb8_FastSimValidation_v2_FSIM/243fe90abe1b1cf7bc2119dc7c0b2e28/output_Skim_noSlim_99_2_aN4.root'
    )
)

process.PDFweigts = cms.EDProducer('PDFweightsProducer',
	# max 3 PDF sets and they have to be in decreasing order of eigenvectors
#	PDFSets				=	cms.vstring('CT10.LHgrid','cteq66.LHgrid','MSTW2008nlo68cl.LHgrid')
#	PDFSets				=	cms.vstring('cteq66.LHgrid')
	PDFSets				=	cms.vstring('cteq66.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
#	PDFSets				=	cms.vstring('cteq66.LHgrid','CT10.LHgrid')
#	PDFSets				=	cms.vstring('NNPDF21_100.LHgrid','CT10.LHgrid','MSTW2008nlo68cl.LHgrid') #ok
#	PDFSets				=	cms.vstring('CT10.LHgrid','cteq66.LHgrid')

)

process.p = cms.Path( process.PDFweigts )


process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile10_x.root')
)


process.e = cms.EndPath(process.out)
