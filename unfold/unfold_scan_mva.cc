#include "TCanvas.h"
#include "TH1F.h"
#include "TH2F.h"
#include "TFile.h"
#include "TRandom3.h"
#include "TUnfold.h"
#include "TUnfoldSys.h"
#include <TVector.h>
#include <TMatrix.h>
#include <TMath.h>
#include "TMinuit.h"
#include <iostream>

#include "unfold.hpp"
#include "utils.hpp"
#include "binnings.h"

using namespace std;

// global makes life easier
Double_t tau = 0;

Double_t asy_err = 0;

Double_t unfold_syst(TString syst, TH1F *hrec, TH2F *hgenrec, TH1F *heff, TH1F *hgen, TFile *f)
{
	// only show errors
	gErrorIgnoreLevel = kError;

	//cout << "using TUnfold " << TUnfold_VERSION << endl;
	
	// dummy canvas
	TCanvas *c1 = new TCanvas("canvas","canvas");
	c1->Clear();
	
	TRandom3 random(0);

	TH1::SetDefaultSumw2(true);

	TFile *fo = new TFile("histos/unfolded_syst_"+syst+".root","RECREATE");
	
	// Background subtraction
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<Float_t> preds;
	vector<TH1F*> bkghistos;
	TH1F *hsignal;

	vector<TH1F*> eigenhistos;
	vector<Float_t> eigenerrors;

	Int_t nbkgs = 0;
	Float_t sum_nonrot = 0;

	// Order of fit results must be the same as in covariance matrix:
	// first entry beta_signal, rest alphabetic
	if(syst == "nominal") 
		read_fitres("nominal",names,scales,uncs);
	else
		read_fitres("syst_"+syst,names,scales,uncs);
	
	nbkgs = names.size()-1;

	// Try to read in systematic sample, otherwise use nominal
	hsignal = (TH1F*)f->Get(var_y+"__tchan__"+syst);
	if(hsignal == NULL) {
		hsignal = (TH1F*)f->Get(var_y+"__tchan");
	}
	hsignal->Scale(scales[0]);

	// Read in background histograms
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		// Try to read in systematic sample, otherwise use nominal
		TH1F *histo = NULL;
		histo = (TH1F*)f->Get(var_y+"__"+name+"__"+syst);
		if(histo == NULL) {
			//cout << "syst not available: " << name << endl;
			histo = (TH1F*)f->Get(var_y+"__"+name);
		}

		// Scale histos
		histo->Scale(scales[i+1]);
		preds.push_back(histo->Integral());
		
		sum_nonrot += histo->Integral();
		bkghistos.push_back((TH1F*)histo);

	}
	//cout << "background events: " << sum_nonrot << endl;
	
	// Decorrelate background templates
	// Read in covariance matrix
	// use systematic covariance matrix
	//TFile *fcov = new TFile("fitresults/cov_syst_"+syst+".root");
	TFile *fcov = new TFile("cov.root"); // FIXME very similar results and fit converges without cov
	TH2D *hcov = (TH2D*)fcov->Get("covariance");
	
	TMatrixD covmatrix(nbkgs,nbkgs);

	// Fill cov matrix, skip first entry with beta_signal
	for(int i = 0; i < nbkgs ; i++) {
		for(int j = 0; j < nbkgs; j++) {
			covmatrix[i][j] = hcov->GetBinContent(i+2,j+2);
		}
	}

	fcov->Close();

	TVectorD eigenvalues(nbkgs);
	TMatrixD eigenvectors = covmatrix.EigenVectors(eigenvalues);
	
	// Unit vector
	TVectorD unitvec(nbkgs);
	for(int i = 0; i < nbkgs; i++) unitvec[i] = 1;
	
	// Inverted eigenvectors
	TMatrixD inv_eigenvectors(eigenvectors);
	inv_eigenvectors.Invert();

	unitvec *= inv_eigenvectors;
	// Scale vector to keep norm
	TVectorD scale_vector(unitvec);
	
	// Apply scale factors to eigenvectors
	for(int i = 0; i < nbkgs; i++)
	{
		for(int j = 0; j < nbkgs; j++)
		{
			eigenvectors[i][j] *= scale_vector[j];
		}
	}

	Float_t sum_rot = 0;
	// Rotate backgrounds
	for(int i = 0; i < nbkgs; i++)
	{
		TH1F *eigenhisto = (TH1F*)bkghistos[i]->Clone();
		eigenhisto->Reset();

		// Add up eigenhistos
		for(int j = 0; j < nbkgs; j++)
		{
			// First index: row, element of vector
			// Second index: column, index of vector
			eigenhisto->Add(bkghistos[j], eigenvectors(j,i));
		}
		eigenhistos.push_back((TH1F*)eigenhisto);
		sum_rot += eigenhisto->Integral();
		//cout << "eigenhisto" << i << " " << eigenhisto->Integral() << endl;
		eigenerrors.push_back(sqrt(eigenvalues[i]));
		// eigenerrors
		//cout << eigenerrors[i] << endl;
	}
	//cout << "background events rotated: " << sum_rot << endl;

	// Number of expected events
	Float_t expected = (hrec->Integral() - sum_nonrot);

	// Scale generated and migration matrix to expected
	hgen->Scale(expected/hgen->Integral()); // for bias
	hgenrec->Scale(expected/hgenrec->Integral());
	
	TH1F *hgen_produced = (TH1F*)hgen->Clone("hgen_produced");

	// Fill overflow bins of mig. matrix with # nonselected events
	for(Int_t i = 1; i <= bin_x; i++) {
		Float_t bin_eff = heff->GetBinContent(i);
		hgen_produced->SetBinContent(i,hgen->GetBinContent(i)/bin_eff);
		Float_t nonsel = hgen_produced->GetBinContent(i)*(1-bin_eff);
		hgenrec->SetBinContent(i,0,nonsel);
	}
	
	// Calculate selection efficiency
	//Float_t overflow = hgenrec->Integral(1,bin_x,0,0);
//	Float_t sel_eff = hgenrec->Integral(1,bin_x,1,bin_y)/overflow;

	//cout << "data events: " << hrec->Integral() << endl;
	//cout << "expected signal events: " << expected << endl;
	//cout << "matrix integral " << hgenrec->Integral() << endl;
	//cout << "Unfolding: " + varname << endl;
		
	// Prepare unfolding
	TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeCurvature);
	//TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeNone);

	// set input distribution
	unfold.SetInput(hrec);
	
	// set bias dist
	//unfold.SetBias(hgen);

	// subtract backgrounds
	for(int i = 0; i < nbkgs; i++)
	{
		unfold.SubtractBackground(eigenhistos[i],names[i+1],1.0, eigenerrors[i]);
		//unfold.SubtractBackground(bkghistos[i],names[i+1],1.0, uncs[i+1]); // FIXME cross check
	}

	// find minimal global correlation
	if(syst == "nominal" && tau == 0) {
		minimizeRhoAverage(&unfold, hrec, 1000, -5, 0); // FIXME check TUnfold version
		tau = unfold.GetTau();
	}
	//Float_t tau = 2.12101e-05; // FIXME get from MC ele
	//Float_t tau = 3.36002e-05;// FIXME get from MC mu
	//cout << "tau: " << tau << endl;

	//Float_t corr;
	//corr = unfold.DoUnfold(tau,hrec, scaleBias);
	unfold.DoUnfold(tau,hrec, scaleBias);

	//cout << "global correlation: " << corr << endl;

	fo->cd();

	TH1F *hurec = new TH1F("unfolded","unfolded",bin_x,var_min,var_max);
	unfold.GetOutput(hurec);

	//cout << "selection eff: " << sel_eff << endl;
	//cout << "reconstructed: " << expected << " unfolded: " << hurec->Integral() << endl;

	// rho, error matrix
	TH2D *hrhoij = new TH2D("correlation","correlation",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetRhoIJ(hrhoij);
	TH2D *hematrix = new TH2D("error","error",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetEmatrix(hematrix);
	// Add migration matrix stat. error
	//unfold.GetEmatrixSysUncorr(hematrix, 0, false); 

	// write results
	hurec->Write();
	hrhoij->Write();
	hematrix->Write();

	Double_t asy = asymmetry(hurec);

	if(syst == "nominal") {
		unfold.GetEmatrixSysUncorr(hematrix, 0, false);  // FIXME
		TH2F* herr = (TH2F*)hematrix;
		asy_err = error_unfold(herr,hurec);
	}
	
	delete c1;
	fo->Close();

	return asy;

}
int main()
{
	vector<TString> samples;
	samples.push_back("mu__cos_theta__mva_-0_5__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_49__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_48__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_47__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_46__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_45__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_44__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_43__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_42__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_41__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_4__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_39__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_38__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_37__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_36__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_35__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_34__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_33__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_32__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_31__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_3__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_29__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_28__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_27__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_26__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_25__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_24__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_23__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_22__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_21__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_2__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_19__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_18__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_17__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_16__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_15__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_14__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_13__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_12__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_11__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_1__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_09__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_08__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_07__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_06__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_05__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_04__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_03__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_02__no_metphi");
	samples.push_back("mu__cos_theta__mva_-0_01__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_0__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_01__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_02__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_03__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_04__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_05__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_06__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_07__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_08__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_09__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_1__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_11__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_12__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_13__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_14__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_15__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_16__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_17__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_18__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_19__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_2__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_21__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_22__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_23__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_24__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_25__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_26__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_27__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_28__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_29__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_3__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_31__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_32__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_33__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_34__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_35__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_36__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_37__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_38__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_39__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_4__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_41__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_42__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_43__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_44__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_45__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_46__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_47__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_48__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_49__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_5__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_51__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_52__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_53__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_54__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_55__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_56__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_57__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_58__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_59__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_6__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_61__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_62__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_63__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_64__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_65__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_66__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_67__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_68__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_69__no_metphi");
	samples.push_back("mu__cos_theta__mva_0_7__no_metphi");

	/*
	samples.push_back("ele__cos_theta__mva_-0_5__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_49__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_48__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_47__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_46__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_45__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_44__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_43__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_42__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_41__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_4__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_39__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_38__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_37__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_36__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_35__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_34__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_33__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_32__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_31__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_3__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_29__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_28__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_27__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_26__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_25__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_24__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_23__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_22__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_21__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_2__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_19__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_18__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_17__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_16__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_15__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_14__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_13__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_12__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_11__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_1__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_09__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_08__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_07__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_06__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_05__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_04__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_03__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_02__no_metphi");
	samples.push_back("ele__cos_theta__mva_-0_01__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_0__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_01__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_02__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_03__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_04__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_05__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_06__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_07__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_08__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_09__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_1__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_11__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_12__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_13__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_14__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_15__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_16__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_17__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_18__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_19__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_2__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_21__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_22__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_23__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_24__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_25__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_26__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_27__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_28__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_29__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_3__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_31__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_32__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_33__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_34__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_35__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_36__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_37__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_38__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_39__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_4__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_41__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_42__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_43__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_44__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_45__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_46__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_47__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_48__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_49__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_5__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_51__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_52__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_53__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_54__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_55__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_56__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_57__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_58__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_59__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_6__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_61__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_62__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_63__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_64__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_65__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_66__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_67__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_68__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_69__no_metphi");
	samples.push_back("ele__cos_theta__mva_0_7__no_metphi");
	*/

	vector<TString> systematics;
	systematics.push_back("nominal");
	systematics.push_back("En__up");
//	systematics.push_back("En__down");
	systematics.push_back("UnclusteredEn__up");
//	systematics.push_back("UnclusteredEn__down");
	systematics.push_back("Res__up");
//	systematics.push_back("Res__down");

	systematics.push_back("leptonID__up");
//	systematics.push_back("leptonID__down");
//	systematics.push_back("leptonIso__up");
//	systematics.push_back("leptonIso__down");
	systematics.push_back("leptonTrigger__up");
//	systematics.push_back("leptonTrigger__down");
	systematics.push_back("pileup__up");
//	systematics.push_back("pileup__down");
	systematics.push_back("btaggingBC__up");
//	systematics.push_back("btaggingBC__down");
	systematics.push_back("btaggingL__up");
//	systematics.push_back("btaggingL__down");
	systematics.push_back("ttbar_scale__up");
//	systematics.push_back("ttbar_scale__down");
	systematics.push_back("ttbar_matching__up");
//	systematics.push_back("ttbar_matching__down");
	systematics.push_back("wjets_shape__up");
//	systematics.push_back("wjets_shape__down");
	systematics.push_back("wjets_flat__up");
//	systematics.push_back("wjets_flat__down");
	
//	systematics.push_back("iso__up");
//	systematics.push_back("iso__down");
	systematics.push_back("mass__up");
//	systematics.push_back("mass__down");
	systematics.push_back("tchan_scale__up");
//	systematics.push_back("tchan_scale__down");
	systematics.push_back("top_pt__up");
//	systematics.push_back("top_pt__down");

	TString dir = "no_QCD_MC_error/";

	for(vector<TString>::iterator it = samples.begin(); it != samples.end(); it++) {

		sample = (*it);

		Double_t asy_nom = 0;
		Double_t unc = 0;
		// load histograms
		TFile *f2 = new TFile("histos/"+dir+sample+"/data.root");
		// DATA
		TH1F *hrec = (TH1F*)f2->Get(var_y+"__DATA");

		cout << sample << endl;

		for(vector<TString>::iterator it2 = systematics.begin(); it2 != systematics.end(); it2++) {
			// systematic reconstructed, subtracted, matrix, efficiency, bias
			TString syst = (*it2);
			//cout << syst << endl;
			if(syst.Contains("ttbar_scale") or syst.Contains("ttbar_matching") or syst.Contains("wjets_shape") or syst.Contains("wjets_flat") or syst.Contains("iso"))
				syst = "nominal";
			TFile *f = new TFile("histos/"+dir+sample+"/rebinned_"+syst+".root");
			TH1F *heff = (TH1F*)f->Get("efficiency");
			TH2F *hgenrec = (TH2F*)f->Get("matrix");
			TH1F *hgen = (TH1F*)f->Get("hgen");
		
			Double_t asy = unfold_syst((*it2),hrec,hgenrec,heff,hgen,f2);
			if(syst == "nominal" && asy_nom == 0) asy_nom = asy;
			Double_t diff = asy_nom - asy;
			//cout << diff << endl;
			unc += TMath::Power(diff,2);

			f->Close();
		}
		unc = TMath::Sqrt(unc);
		Double_t tot = TMath::Power(asy_err,2) + TMath::Power(unc,2);
		tot = TMath::Sqrt(tot);
		cout << asy_nom << " " << asy_err << " " << unc << " " << tot << endl;
		
		tau = 0;
		asy_nom = 0;
		f2->Close();
	}

}
