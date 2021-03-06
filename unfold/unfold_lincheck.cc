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

// Number of pseudo experiments
#define NPSEUDO 50000
//#define NPSEUDO 1000

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

Double_t unfold(TString asym, TH1F *hrec, TH2F *hgenrec, TH1F *heff, TH1F *hgen, TFile *f)
{
	// only show errors
	gErrorIgnoreLevel = kError;

	//cout << "using TUnfold " << TUnfold_VERSION << endl;
	
	// dummy canvas
	TCanvas *c1 = new TCanvas("canvas","canvas");
	c1->Clear();
	
	TRandom3 random(0);

	TH1::SetDefaultSumw2(true);

	TFile *fo = new TFile("histos/unfolded_"+asym+".root","RECREATE");
	
	bool subtractData = true;
	//bool subtractData = false;

	//bool do_pseudo = false; // FIXME
	bool do_pseudo = true; // FIXME

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

	if(subtractData) {
		
		// Order of fit results must be the same as in covariance matrix:
		// first entry beta_signal, rest alphabetic
		read_fitres("nominal",names,scales,uncs);
				
		nbkgs = names.size()-1;

		hsignal = (TH1F*)f->Get(var_y+"__tchan");
		hsignal->Scale(scales[0]);

		// Read in background histograms
		for(int i = 0; i < nbkgs ; i++) {
			TString name = names.at(i+1);
			TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
			
			// Scale histos
			histo->Scale(scales[i+1]);
			preds.push_back(histo->Integral());
			
			sum_nonrot += histo->Integral();
			bkghistos.push_back((TH1F*)histo);

		}
		//cout << "background events: " << sum_nonrot << endl;

		// Decorrelate background templates
		// Read in covariance matrix
		TFile *fcov = new TFile("cov.root");
		TH2D *hcov = (TH2D*)fcov->Get("covariance");
		
		TMatrixD covmatrix(nbkgs,nbkgs);

		// Fill cov matrix, skip first entry with beta_signal
		for(int i = 0; i < nbkgs ; i++) {
			//TString name = hcov->GetXaxis()->GetBinLabel(i+2);
			//cout << name << endl;
			//cout << names.at(i+1) << endl;
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
			//eigenerrors.push_back(sqrt(eigenvalues[i]) / eigenhisto->Integral());
			eigenerrors.push_back(sqrt(eigenvalues[i]));
			// eigenerrors
			//cout << eigenerrors[i] << endl;
		}
		//cout << "background events rotated: " << sum_rot << endl;
	}

	// Current samples are normalized to one
	Float_t expected = 4617; // Events expected in data: approx at 20/fb
	if(!subtractData) hrec->Scale(expected/hrec->Integral());

	// Number of expected events
	if(subtractData)
		expected = (hrec->Integral() - sum_nonrot);
	else
		expected = hrec->Integral();

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
//	Float_t overflow = hgenrec->Integral(1,bin_x,0,0);
//	Float_t sel_eff = hgenrec->Integral(1,bin_x,1,bin_y)/overflow;

//	cout << "data events: " << hrec->Integral() << endl;
//	cout << "expected signal events: " << expected << endl;
//	cout << "matrix integral " << hgenrec->Integral() << endl;
//	cout << "Unfolding: " + varname << endl;
		
	// Prepare unfolding
	TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeCurvature);
	//TUnfoldSys unfold(hgenrec,TUnfold::kHistMapOutputHoriz,TUnfold::kRegModeNone); // FIXME For tests

	// set input distribution
	unfold.SetInput(hrec);
	
	// set bias dist
	//unfold.SetBias(hgen_produced);

	// subtract backgrounds
	if(subtractData) {
		for(int i = 0; i < nbkgs; i++)
		{
			unfold.SubtractBackground(eigenhistos[i],names[i+1],1.0, eigenerrors[i]);
			//unfold.SubtractBackground(bkghistos[i],names[i+1],1.0, uncs[i+1]); // FIXME Test subtracting nominal histos
		}
	}


	// find minimal global correlation // FIXME
	minimizeRhoAverage(&unfold, hrec, 1000, -5, 0); // mu
	//minimizeRhoAverage(&unfold, hrec, 1000, -6, 0); // ele
	Float_t tau = unfold.GetTau();

	cout << "tau: " << tau << endl;

	Float_t corr;
	corr = unfold.DoUnfold(tau,hrec, scaleBias);

	cout << "global correlation: " << corr << endl;

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
	unfold.GetEmatrixSysUncorr(hematrix, 0, false); 

	//Double_t asy = asymmetry(hurec);

	//cout << "unfolded asymmetry: " << asy << endl;

	//return asy;

	// pseudo experiments
	TH1F *hPull[bin_x];
	TH1F *hBin[bin_x];
	TH1F hStatErr("staterr","staterr",1000,0.0,1.0);
	TH1F hasy("asymmetry","asymmetry",100,0.0,1.0);
	TH1F hasy_bias("asymmetry_bias","asymmetry_bias",100,-1.0,1.0);
	TH1F hasy_pull("asymmetry_pull","asymmetry_pull",100,-3.0,3.0);

	TString pull_name = "pull_";
	TString bin_name = "reldiff_";
	for(Int_t i=1; i <= bin_x; i++) {
		TString pname = pull_name;
		pname += i;
		TString bname = bin_name;
		bname += i;
		hPull[i-1] = new TH1F(pname,pname,60,-3.0,3.0);
		hBin[i-1] = new TH1F(bname,bname,100,-1.0,1.0);
	}
	
	// do PEs
	if (do_pseudo) {
	cout << "Dicing " << NPSEUDO << " pseudo events..." << endl;
	Float_t genasy = asymmetry(hgen_produced);
	//cout << "Generated asymmetry: " << genasy << endl;
	//TH1F *hpseudo = new TH1F("pseudo","pseudo", bin_y, list_y);
	TH1F *hpseudo = new TH1F("pseudo","pseudo", bin_y, var_min, var_max);
	for(Int_t p=1; p<=NPSEUDO; p++) {
		
		if(p%5000 == 0) cout << p << endl;
		
		hpseudo->Reset();
		if(subtractData) {
			for(int i = 0; i < nbkgs ; i++) {
				TH1F *heigen = (TH1F*)eigenhistos[i];
				//TH1F *heigen = (TH1F*)bkghistos[i]; // FIXME Test dicing nominal
				TH1F *hclone = (TH1F*)heigen->Clone();
				
				Float_t bla = random.Gaus(heigen->Integral(),eigenerrors[i]*heigen->Integral());
				//Float_t bla = random.Gaus(heigen->Integral(),uncs[i+1]*heigen->Integral()); // FIXME test dicing nominal
				
				int n = random.Poisson(bla);
				
				for(int ibin = 1; ibin <= bin_y; ibin++) {
					Float_t val = hclone->GetBinContent(ibin);
					Float_t err = hclone->GetBinError(ibin);
					hclone->SetBinContent(ibin, random.Gaus(val, err));
				}

				for(int j = 0; j < n; j++) {
					hpseudo->Fill(hclone->GetRandom());
				}
				delete hclone;
			}
			int n = random.Poisson(hsignal->Integral());
			TH1F *hclone = (TH1F*)hsignal->Clone();
			for(int ibin = 1; ibin <= bin_y; ibin++) {
					Float_t val = hclone->GetBinContent(ibin);
					Float_t err = hclone->GetBinError(ibin);
					hclone->SetBinContent(ibin, random.Gaus(val, err));
			}
			for(int j = 0; j < n; j++) {
				hpseudo->Fill(hclone->GetRandom());
			}
			delete hclone;
		} else {
			int n = random.Poisson(hrec->Integral());
			TH1F *hclone = (TH1F*)hrec->Clone();
			/*
			for(int ibin = 1; ibin <= bin_y; ibin++) {
					Float_t val = hclone->GetBinContent(ibin);
					Float_t err = hclone->GetBinError(ibin);
					hclone->SetBinContent(ibin, random.Gaus(val, err));
			}
			*/

			for(int j = 0; j < n; j++) {
				hpseudo->Fill(hclone->GetRandom());
			}
			delete hclone;
		}
		
		unfold.SetInput(hpseudo);

		unfold.DoUnfold(tau,hpseudo,scaleBias);
		TH1F *hupseudo = new TH1F("upseudo","pseudo unfolded",bin_x,var_min,var_max);
		unfold.GetOutput(hupseudo);
		// Ematrix not containing all errors,
		// check http://root.cern.ch/root/html/TUnfoldSys.html
		TH2F *hperr = new TH2F("perror","perror",bin_x,1,bin_x,bin_x,1,bin_x);
		unfold.GetEmatrix(hperr);
		// Add migration matrix stat. error
		unfold.GetEmatrixSysUncorr(hperr, 0, false); 
		

		// Calculate asymmetry
		Float_t asy = asymmetry(hupseudo);
		hasy.Fill(asy);
		Float_t asy_diff = genasy - asy;
		hasy_bias.Fill(asy_diff/genasy);
		Float_t perror = error_unfold(hperr,hupseudo);
		hStatErr.Fill(perror);
		hasy_pull.Fill(asy_diff/perror);

		// pull, rel. diff.
		for(Int_t k=1; k<=bin_x; k++) {
			Float_t diff = (hgen_produced->GetBinContent(k) - hupseudo->GetBinContent(k));
			
			hPull[k-1]->Fill(diff/hupseudo->GetBinError(k));
			hBin[k-1]->Fill(diff/hgen_produced->GetBinContent(k));
		}
		delete hperr;
		delete hupseudo;
	}
	// end pseudo
	} 
	
	cout << "Unfolded asymmetry: " << hasy.GetMean() << endl;

	// write results
	hurec->Write();
	hrhoij->Write();
	hematrix->Write();
	
	// pseudo exp results
	if(do_pseudo) {
		hasy.Write();
		hasy_bias.Write();
		hasy_pull.Write();
		hStatErr.Write();

		// write pull, bin histos
		for(Int_t i=0; i < bin_x; i++) {
			hBin[i]->Write();
			hPull[i]->Write();
		}
	}

	fo->Close();

	return hasy.GetMean();
}

void pseudodata(TString nominal)
{
	TFile *f = new TFile("histos/"+nominal+"/data.root");
	TFile *f1 = new TFile("histos/"+sample+"/rebinned_nominal.root");
	TFile *fo = new TFile("histos/"+sample+"/pseudo_data.root","RECREATE");
	fo->cd();
	
	vector<TString> names;
	vector<Float_t> scales;
	vector<Float_t> uncs;
	vector<TH1F*> histos;

	read_fitres("nominal",names,scales,uncs);
	Int_t nbkgs = names.size()-1;
	
	TH1::SetDefaultSumw2(true);
	//TH1F *hsignal = (TH1F*)f->Get(var_y+"__tchan");
	TH1F *hin = (TH1F*)f1->Get("hrec");
	TH1F *hsignal = (TH1F*)hin->Clone(var_y+"__tchan");
	//hsignal->Scale(scales[0]);
	// Artificially enhance signal fraction
	// FIXME
	//hsignal->Scale(2);
	hsignal->Write();
	TH1F *added = (TH1F*)hsignal->Clone(var_y+"__DATA");
	
	// Read in background histograms
	for(int i = 0; i < nbkgs ; i++) {
		TString name = names.at(i+1);
		TH1F *histo = (TH1F*)f->Get(var_y+"__"+name);
				
		// Scale histos
		//histo->Scale(scales[i+1]);
		added->Add(histo);
		histo->Write();
	}

	//cout << added->Integral() << endl;
	fo->cd();
	added->Write();
	fo->Close();
}

int main()
{ 
	/*
	TString nominal = "no_metphi/mu__cos_theta__mva_0_06__no_metphi";
	vector<TString> samples;
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.2__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.25__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.3__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.35__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.4__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.45__no_metphi");
	samples.push_back("no_metphi/mu__cos_theta__mva_0_06__asymm_0.5__no_metphi");
	*/

	TString nominal = "no_metphi/ele__cos_theta__mva_0_13__no_metphi";
	vector<TString> samples;
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.2__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.25__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.3__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.35__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.4__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.45__no_metphi");
	samples.push_back("no_metphi/ele__cos_theta__mva_0_13__asymm_0.5__no_metphi");

	Int_t asym_count = 20;

        ofstream ofs;
        ofs.open("lincheck.txt");

	for(vector<TString>::iterator it = samples.begin(); it != samples.end(); it++) {
		sample = (*it);
		cout << sample << endl;

		TString asym = "asym_";
		asym += asym_count;
		
		pseudodata(nominal);

		// load histograms
		TFile *f2 = new TFile("histos/"+sample+"/pseudo_data.root");
		TH1F *hrec = (TH1F*)f2->Get(var_y+"__DATA");
		
		TFile *f = new TFile("histos/"+nominal+"/rebinned_nominal.root");
		TH1F *heff = (TH1F*)f->Get("efficiency");
		TH2F *hgenrec = (TH2F*)f->Get("matrix");
		TH1F *hgen = (TH1F*)f->Get("hgen");
		
		TFile *f1 = new TFile("histos/"+sample+"/rebinned_nominal.root");
		TH1F *hgen_presel = (TH1F*)f1->Get("hgen_presel");
		Double_t genasy = asymmetry(hgen_presel);
		
		Double_t unfasy = unfold(asym,hrec,hgenrec,heff,hgen,f2);

		cout << asym_count << " " << genasy << " " << unfasy << endl;
		ofs << genasy << " " << unfasy << endl;

	
		f->Close();
	
		asym_count += 5;
	}

	ofs.close();
	
}
