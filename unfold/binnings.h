#ifndef BINNINGS_H
#define BINNINGS_H
#include "TString.h"

// Number of reconstructed bins should be twice as much as generated
// x: generated
// y: reconstructed
// cosTheta

TString varname = "cos#theta_{l,j}";
TString var_x = "true_cos_theta";
TString var_y = "cos_theta";
const Double_t var_min = -1;
const Double_t var_max = 1;

//const Int_t bin_x = 8;
//const Int_t bin_y = 16;

const Int_t bin_x = 6;
const Int_t bin_y = 12;


//TString sample = "allsyst/mu__cos_theta__mva_0_06__no_metphi";
//TString sample = "allsyst/mu__cos_theta__mva_0_06__comphep__no_metphi";

//TString sample = "allsyst/ele__cos_theta__mva_0_13__no_metphi";
//TString sample = "allsyst/ele__cos_theta__mva_0_13__comphep__no_metphi";

TString sample = "no_powheg_fix/mu__cos_theta__mva_0_06__no_powheg_fix";
//TString sample = "no_powheg_fix/ele__cos_theta__mva_0_13__no_powheg_fix";

//TString sample = "wjets/mu__cos_theta__mva_0_06__wjets";
//TString sample = "wjets/ele__cos_theta__mva_0_13__wjets";

// FIXME cross check
//TString sample = "QCD_fixed/mu__cos_theta__mva_0_06__qcdfixed";

#endif
