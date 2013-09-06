#include <TString.h>
#include <TFile.h>
#include <TH1F.h>
#include <TH2F.h>
#include <TMath.h>
#include <iostream>

#include "utils.hpp"
#include "binnings.h"

using namespace std;

Double_t calc_asymmetry_syst(TString syst)
{
	TFile *f1 = new TFile("histos/unfolded.root");
	TFile *f2 = new TFile("histos/unfolded_syst_"+syst+".root");

	TH1F *hunf_nom = (TH1F*)f1->Get("unfolded");
	TH1F *hunf_syst = (TH1F*)f2->Get("unfolded");
	
	// unfolded in bins of generated
	TH1F *hunf_nom_rebin = new TH1F(var_y+"_unf_nom",var_y+"_unf_nom",bin_x,var_min,var_max);
	for(Int_t i = 1; i <= bin_x; i++) {
		hunf_nom_rebin->SetBinContent(i,hunf_nom->GetBinContent(i));
		hunf_nom_rebin->SetBinError(i,hunf_nom->GetBinError(i));
	}
	
	TH1F *hunf_syst_rebin = new TH1F(var_y+"_unf_syst",var_y+"_unf_syst",bin_x,var_min,var_max);
	for(Int_t i = 1; i <= bin_x; i++) {
		hunf_syst_rebin->SetBinContent(i,hunf_syst->GetBinContent(i));
		hunf_syst_rebin->SetBinError(i,hunf_syst->GetBinError(i));
	}


	Double_t asy_nom = asymmetry(hunf_nom_rebin);
	Double_t asy_syst = asymmetry(hunf_syst_rebin);

//	cout << endl << asy_nom << " " << asy_syst << endl;

	Double_t diff = asy_nom - asy_syst;
	//Double_t uncertainty = diff/asy_nom; // FIXME relative
	Double_t uncertainty = diff;
	//cout << uncertainty << endl;

	return uncertainty;
}

int main()
{	
	vector<TString> systematics;
	/*
	systematics.push_back("En");
	systematics.push_back("UnclusteredEn");
	systematics.push_back("Res");

	systematics.push_back("leptonID");
	systematics.push_back("leptonIso");
	systematics.push_back("leptonTrigger");
	systematics.push_back("pileup");
	systematics.push_back("btaggingBC");
	systematics.push_back("btaggingL");
	systematics.push_back("ttbar_scale");
	systematics.push_back("ttbar_matching");
	systematics.push_back("wjets_shape");
	systematics.push_back("wjets_flat");

	systematics.push_back("iso");
	systematics.push_back("mass");
	systematics.push_back("tchan_scale");
	systematics.push_back("top_pt");
	systematics.push_back("pdf");
	systematics.push_back("lepton_weight_shape");
	
	systematics.push_back("DYJets_fraction");
	systematics.push_back("QCD_fraction");
	systematics.push_back("Dibosons_fraction");
	systematics.push_back("s_chan_fraction");
	systematics.push_back("tW_chan_fraction");
	*/
	
	//systematics.push_back("wjets_FSIM_scale");
	//systematics.push_back("wjets_FSIM_matching");
	//systematics.push_back("pdf");
	//systematics.push_back("mass");
	systematics.push_back("tchan_scale");

	Double_t uncertainty = 0;
	Double_t tot_unc_up = 0;
	Double_t tot_unc_down = 0;

        for(vector<TString>::iterator it = systematics.begin(); it != systematics.end(); it++) {
		cout << (*it) << "\t";
		TString up = (*it);
		up += "__up";
		TString down = (*it);
		down += "__down";
		//Double_t unc_up = TMath::Power(calc_asymmetry_syst(up),2);
		Double_t unc_up = calc_asymmetry_syst(up);
		Double_t unc_down = calc_asymmetry_syst(down);
		cout << unc_up << "\t" << unc_down << endl;
		
		if(fabs(unc_up) > fabs(unc_down))
			uncertainty += TMath::Power(unc_up, 2);
		else 
			uncertainty += TMath::Power(unc_down, 2);

		tot_unc_up += TMath::Power(unc_up, 2);
		tot_unc_down += TMath::Power(unc_up, 2);
	}
	cout << "========================" << endl;
	//cout << "relative total uncertainty: " << TMath::Sqrt(uncertainty) << endl;
	cout << "total uncertainty: " << TMath::Sqrt(uncertainty) << endl;
	cout << "total uncertainty (up): " << TMath::Sqrt(tot_unc_up) << endl;
	cout << "total uncertainty (down): " << TMath::Sqrt(tot_unc_down) << endl;

	return 0;
}
