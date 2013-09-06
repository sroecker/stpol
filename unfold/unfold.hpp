#ifndef UNFOLD_HPP
#define UNFOLD_HPP

#include "TMath.h"
#include "TH1F.h"
#include "TUnfold.h"
#include "TUnfoldSys.h"
#include "TMinuit.h"

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

#endif
