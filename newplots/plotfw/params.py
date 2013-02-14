import ROOT
from cross_sections import xs

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
