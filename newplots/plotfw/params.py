import ROOT
from cross_sections import xs
from methods import Cut

colors = {
	"T_t": ROOT.kRed,
	"Tbar_t": ROOT.kRed,
	"T_tW": ROOT.kYellow+4,
	"Tbar_tW": ROOT.kYellow+4,
	"T_s": ROOT.kYellow,
	"Tbar_s": ROOT.kYellow,

	"WJets": ROOT.kGreen,
	"W1Jets": ROOT.kGreen+1,
	"W2Jets": ROOT.kGreen+2,
	"W3Jets": ROOT.kGreen+3,
	"W4Jets": ROOT.kGreen+4,

	"WW": ROOT.kBlue,
	"WZ": ROOT.kBlue,
	"ZZ": ROOT.kBlue,

	"TTbar": ROOT.kOrange,

	"QCDMu": ROOT.kGray,

	"QCD_Pt_20_30_EMEnriched": ROOT.kGray,
	"QCD_Pt_30_80_EMEnriched": ROOT.kGray,
	"QCD_Pt_80_170_EMEnriched": ROOT.kGray,
	"QCD_Pt_170_250_EMEnriched": ROOT.kGray,
	"QCD_Pt_250_350_EMEnriched": ROOT.kGray,
	"QCD_Pt_350_EMEnriched": ROOT.kGray,


	"QCD_Pt_20_30_BCtoE": ROOT.kGray,
	"QCD_Pt_30_80_BCtoE": ROOT.kGray,
	"QCD_Pt_80_170_BCtoE": ROOT.kGray,
	"QCD_Pt_170_250_BCtoE": ROOT.kGray,
	"QCD_Pt_250_350_BCtoE": ROOT.kGray,
	"QCD_Pt_350_BCtoE": ROOT.kGray,

	"SingleMu": ROOT.kBlack,
	"SingleEle": ROOT.kBlack,
}

# Selection applied as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=228739
class Cuts:
	initial = Cut("postSkim", "1==1")

	recoFState = Cut("recoFstate", "_topCount==1")
	mu  = Cut("mu", "_muonCount==1") \
	    * Cut("muIso", "_goodSignalMuons_0_relIso<0.12") \
	    * Cut("looseMuVeto", "_looseVetoMuCount==0") \
	    * Cut("looseEleVeto", "_looseVetoEleCount==0") \
	
	ele = Cut("ele", "_electronCount==1") \
	    * Cut("eleIso", "_goodSignalElectrons_0_relIso<0.3") \
	    * Cut("eleMVA", "_goodSignalElectrons_0_mvaID>0.9") \

	jets_1LJ = Cut("1LJ", "_lightJetCount==1")
	jets_2plusJ = Cut("1plusLJ", "_lightJetCount>=0 && _bJetCount>=0 && (_lightJetCount + _bJetCount)>=2")
	jets_2J1T = Cut("2J1T", "_lightJetCount==1 && _bJetCount==1")
	jets_2J0T = Cut("2J0T", "_lightJetCount==1 && _bJetCount==0")
	jets_3J1T = Cut("3J1T", "_lightJetCount==2 && _bJetCount==1")
	jets_3J2T = Cut("3J2T", "_lightJetCount==2 && _bJetCount==2")
	realSol = Cut("realSol", "solType_recoNuProducerMu==0")
	cplxSol = Cut("cplxSol", "solType_recoNuProducerMu==1")
	mlnu = Cut("ml#nu", "_recoTop_0_Mass>130&&_recoTop_0_Mass<220")
	etaLJ = Cut("#eta_{lj}", "abs(_lowestBTagJet_0_Eta)>2.5")
	sidebandRegion = Cut("!ml#nu", "!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)")
	jetPt = Cut("jetPt", "_goodJets_0_Pt>40 && _goodJets_1_Pt>40")
	jetEta = Cut("jetEta", "abs(_lowestBTagJet_0_Eta)<4.5 && abs(_highestBTagJet_0_Eta)<4.5")
	jetRMS = Cut("rms_{lj}", "_lowestBTagJet_0_rms < 0.025")
	MTmu = Cut("MT", "_muAndMETMT > 50")
	MTele = Cut("MT", "_patMETs_0_Pt>45")

	#Orso = mlnu * jets_2J1T * jetPt * jetRMS * MT * etaLJ#jetEta
	Orso = mlnu * jets_2J1T * jetPt * jetRMS * etaLJ * jetEta
	finalMu = mu * recoFState * Orso * MTmu
	finalEle = ele * recoFState * Orso * MTele
