#Compile with
#$ scram b -f SingleTopPolarization/Analysis
#Output will be in $CMSSW_DIR/bin/
import FWCore.ParameterSet.Config as cms

process = cms.Process("STPOLSEL3")
process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.options = cms.untracked.PSet(wantSummary=cms.untracked.bool(True))

process.fwliteInput = cms.PSet(
    fileNames   = cms.vstring('/scratch/joosep/step2_MC_Iso_Mar14/WD_T_t/res/output_1_1_SfY.root'),
    maxEvents   = cms.int32(-1),
    outputEvery = cms.uint32(1000),
)

process.fwliteOutput = cms.PSet(
    fileName  = cms.string('analyzeFWLiteHistograms.root'),
)
process.muonAnalyzer = cms.PSet(
    muon_count_src = cms.InputTag("muonCount"),
    veto_muon_count_src = cms.InputTag("looseVetoMuCount"),
    veto_ele_count_src = cms.InputTag("looseVetoEleCount"),
    muon_pt_src = cms.InputTag("goodSignalMuonsNTupleProducer", "Pt"),
    muon_iso_src = cms.InputTag("goodSignalMuonsNTupleProducer", "relIso"),
    mt_mu_src = cms.InputTag("muAndMETMT"),
    mlnu_mass_src = cms.InputTag("recoTopNTupleProducer", "Mass"),
    light_jet_eta_src = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
    light_jet_rms_src = cms.InputTag("lowestBTagJetNTupleProducer", "rms"),
    good_jet_count_src = cms.InputTag("goodJetCount"),
    btag_jet_count_src = cms.InputTag("bJetCount"),
    pdf_weights = cms.InputTag("pdfInfo1", "PDFSet")
)

process.histos = cms.VPSet([
    cms.PSet(
        name=cms.string("eta_lj_mt_mu"),
        var = cms.InputTag("lowestBTagJetNTupleProducer", "Eta"),
        formula=cms.string(""),
        nbins=cms.uint32(100),
        binslow=cms.double(-5),
        binshigh=cms.double(-5),
        cutname=cms.string("mt_mu"),
        srctype=cms.uint32(1), #reads from std::vector<float>
        vecindex=cms.int32(0)
    )
])

