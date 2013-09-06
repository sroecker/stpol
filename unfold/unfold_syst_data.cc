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

#include "utils.hpp"
#include "binnings.h"

using namespace std;

const double scaleBias = 1.0;

TUnfoldSys* myUnfold1d_TUnfoldGlobalPointerForTMinuit;
TH1F* myUnfold1d_hdataGlobalPointerForTMinuit;

static void myUnfold1d_globalFunctionForMinuit(int &npar, double *gin, double &f, double *par, int iflag)
{
  const double logtau = par[0];
  const double scaleBias = par[1];
  myUnfold1d_TUnfoldGlobalPointerForTMinuit->DoUnfold(pow(10, logtau), myUnfold1d_hdataGlobalPointerForTMinuit, scaleBias);
  
  f = myUnfold1d_TUnfoldGlobalPointerForTMinuit->GetRhoAvg();
}



void minimizeRhoAverage(TUnfoldSys *unfold, TH1F *hdata, int nsteps, double log10min, double log10max)
{
  myUnfold1d_TUnfoldGlobalPointerForTMinuit = unfold;
  myUnfold1d_hdataGlobalPointerForTMinuit = hdata;
  
  // Instantiate Minuit for 2 parameters
  TMinuit minuit(2);
  minuit.SetFCN(myUnfold1d_globalFunctionForMinuit);
  minuit.SetPrintLevel(-1); // -1 no output, 1 output
 
  minuit.DefineParameter(0, "logtau", (log10min+log10max)/2, 1, log10min, log10max);
  minuit.DefineParameter(1, "scaleBias", scaleBias, 0, scaleBias, scaleBias);
  minuit.FixParameter(1);
  
  minuit.SetMaxIterations(100);
  minuit.Migrad();
  
  double bestlogtau = -1000;
  double bestlogtau_err = -1000; // error is meaningless because we don't have a likelihood, but method expects it
  minuit.GetParameter(0, bestlogtau, bestlogtau_err);
  unfold->DoUnfold(pow(10, bestlogtau), hdata, scaleBias); 
  
}

void unfold_syst(TString syst, TH1F *hrec, TH2F *hgenrec, TH1F *heff, TH1F *hgen, TFile *f)
{
	// only show errors
	// gErrorIgnoreLevel = kError;

	cout << "using TUnfold " << TUnfold_VERSION << endl;
	
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
	read_fitres("syst_"+syst,names,scales,uncs);
	//read_fitres("nominal",names,scales,uncs); // FIXME cross check
	
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
			cout << "syst not available: " << name << endl;
			histo = (TH1F*)f->Get(var_y+"__"+name);
		}

		// Scale histos
		histo->Scale(scales[i+1]);
		preds.push_back(histo->Integral());
		
		sum_nonrot += histo->Integral();
		bkghistos.push_back((TH1F*)histo);

	}
	cout << "background events: " << sum_nonrot << endl;
	
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
	Float_t overflow = hgenrec->Integral(1,bin_x,0,0);
	Float_t sel_eff = hgenrec->Integral(1,bin_x,1,bin_y)/overflow;

	//cout << "data events: " << hrec->Integral() << endl;
	cout << "expected signal events: " << expected << endl;
	cout << "matrix integral " << hgenrec->Integral() << endl;
	cout << "Unfolding: " + varname << endl;
		
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
	//minimizeRhoAverage(&unfold, hrec, 1000, -5, 0); // FIXME check TUnfold version

	//Float_t tau = unfold.GetTau();
	Float_t tau = 3.11821e-05;// FIXME get from MC mu
	//Float_t tau = 2.08745e-05; // FIXME get from MC ele
	cout << "tau: " << tau << endl;

	Float_t corr;
	corr = unfold.DoUnfold(tau,hrec, scaleBias);

	cout << "global correlation: " << corr << endl;

	fo->cd();

	TH1F *hurec = new TH1F("unfolded","unfolded",bin_x,1,bin_x);
	unfold.GetOutput(hurec);

	cout << "selection eff: " << sel_eff << endl;
	cout << "reconstructed: " << expected << " unfolded: " << hurec->Integral() << endl;

	// rho, error matrix
	TH2D *hrhoij = new TH2D("correlation","correlation",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetRhoIJ(hrhoij);
	TH2D *hematrix = new TH2D("error","error",bin_x,1,bin_x,bin_x,1,bin_x);
	unfold.GetEmatrix(hematrix);
	// Add migration matrix stat. error
	unfold.GetEmatrixSysUncorr(hematrix, 0, false); 

	// write results
	hurec->Write();
	hrhoij->Write();
	hematrix->Write();
	

	fo->Close();

	delete c1;

}

int main()
{

	// load histograms
	TFile *f2 = new TFile("histos/"+sample+"/data.root");
	//
		// DATA
	TH1F *hrec = (TH1F*)f2->Get(var_y+"__DATA");

	vector<TString> systematics;
	/*
	systematics.push_back("En__up");
	systematics.push_back("En__down");
	systematics.push_back("UnclusteredEn__up");
	systematics.push_back("UnclusteredEn__down");
	systematics.push_back("Res__up");
	systematics.push_back("Res__down");

	systematics.push_back("leptonID__up");
	systematics.push_back("leptonID__down");
	systematics.push_back("leptonIso__up");
	systematics.push_back("leptonIso__down");
	systematics.push_back("leptonTrigger__up");
	systematics.push_back("leptonTrigger__down");
	systematics.push_back("pileup__up");
	systematics.push_back("pileup__down");
	systematics.push_back("btaggingBC__up");
	systematics.push_back("btaggingBC__down");
	systematics.push_back("btaggingL__up");
	systematics.push_back("btaggingL__down");
	systematics.push_back("ttbar_scale__up");
	systematics.push_back("ttbar_scale__down");
	systematics.push_back("ttbar_matching__up");
	systematics.push_back("ttbar_matching__down");
	systematics.push_back("wjets_shape__up");
	systematics.push_back("wjets_shape__down");
	systematics.push_back("wjets_flat__up");
	systematics.push_back("wjets_flat__down");
	
	systematics.push_back("iso__up");
	systematics.push_back("iso__down");
	systematics.push_back("mass__up");
	systematics.push_back("mass__down");
	systematics.push_back("tchan_scale__up");
	systematics.push_back("tchan_scale__down");
	systematics.push_back("top_pt__up");
	systematics.push_back("top_pt__down");
	systematics.push_back("pdf__up");
	systematics.push_back("pdf__down");
	systematics.push_back("lepton_weight_shape__up");
	systematics.push_back("lepton_weight_shape__down");

	systematics.push_back("DYJets_fraction__up");
	systematics.push_back("DYJets_fraction__down");
	systematics.push_back("QCD_fraction__up");
	systematics.push_back("QCD_fraction__down");
	systematics.push_back("Dibosons_fraction__up");
	systematics.push_back("Dibosons_fraction__down");
	systematics.push_back("s_chan_fraction__up");
	systematics.push_back("s_chan_fraction__down");
	systematics.push_back("tW_chan_fraction__up");
	systematics.push_back("tW_chan_fraction__down");
	*/
	/*
	systematics.push_back("wjets_FSIM_scale__up");
	systematics.push_back("wjets_FSIM_scale__down");
	systematics.push_back("wjets_FSIM_matching__up");
	systematics.push_back("wjets_FSIM_matching__down");
	*/

	//systematics.push_back("pdf__up");
	//systematics.push_back("pdf__down");
	
	/*
	systematics.push_back("mass__up");
	systematics.push_back("mass__down");
	*/
	systematics.push_back("tchan_scale__up");
	systematics.push_back("tchan_scale__down");

        for(vector<TString>::iterator it = systematics.begin(); it != systematics.end(); it++) {
		// systematic reconstructed, subtracted, matrix, efficiency, bias
		cout << (*it) << endl;
		TString syst = (*it);
		if(syst.Contains("fraction") or syst.Contains("FSIM") or syst.Contains("ttbar_scale") or syst.Contains("ttbar_matching") or syst.Contains("wjets_shape") or syst.Contains("wjets_flat") or syst.Contains("iso"))
			syst = "nominal";
		TFile *f = new TFile("histos/"+sample+"/rebinned_"+syst+".root");
		TH1F *heff = (TH1F*)f->Get("efficiency");
		TH2F *hgenrec = (TH2F*)f->Get("matrix");
		TH1F *hgen = (TH1F*)f->Get("hgen");
	
		unfold_syst(*it,hrec,hgenrec,heff,hgen,f2);
	
		f->Close();
	}
}
