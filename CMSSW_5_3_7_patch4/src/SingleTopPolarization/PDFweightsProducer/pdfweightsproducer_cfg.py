import FWCore.ParameterSet.Config as cms

process = cms.Process("OWNPARTICLES")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/hdfs/cms/store/user/jpata/TTJets_MassiveBinDECAY_TuneZ2star_8TeV-madgraph-tauola/stpol_Feb8_FastSimValidation_v2_FSIM/243fe90abe1b1cf7bc2119dc7c0b2e28/output_Skim_noSlim_99_2_aN4.root'
    )
)

process.myProducerLabel = cms.EDProducer('PDFweightsProducer',
	PDFSetSrc			=	cms.string('CT10.LHgrid'),		# weights of all PDF sets are saved
	PDFSetAlternatives	=	cms.vstring('cteq66.LHgrid'),	# only best fit ratio to PDFSetSrc best fit saved
)

process.out = cms.OutputModule("PoolOutputModule",
    fileName = cms.untracked.string('myOutputFile.root')
)

  
process.p = cms.Path(process.myProducerLabel)

process.e = cms.EndPath(process.out)
