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

const Int_t bin_x = 7;
const Int_t bin_y = 14;

// FIXME use this
// mu mva -0.07
//TString sample = "mu_cos_theta_mva_-0_07";
//Double_t list_x[bin_x+1] = {-1., -0.2264, 0., 0.2268, 0.3904, 0.541, 0.6938, 1.};
//Double_t list_y[bin_y+1] = {-1., -0.4284, -0.1864, 0., 0.0864, 0.1872, 0.2758, 0.3574, 0.436, 0.5088, 0.5754, 0.6426, 0.7134, 0.796, 1.};

// mu mva -0.03
//TString sample = "mu_cos_theta_mva_-0_03";
//Double_t list_x[bin_x+1] = {-1., -0.2262, 0., 0.226, 0.389, 0.5398, 0.6922, 1.};
//Double_t list_y[bin_y+1] = {-1., -0.4278, -0.1852, 0., 0.0866, 0.1874, 0.2758, 0.357, 0.4352, 0.5078, 0.5742, 0.6412, 0.7118, 0.7934, 1. };

// mu mva 0.01
//TString sample = "mu_cos_theta_mva_0_01";
//Double_t list_x[bin_x+1] = {-1., -0.2236, 0., 0.2264, 0.3886, 0.5394, 0.6906, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.4246, -0.1802, 0., 0.0898, 0.1904, 0.2778, 0.3584, 0.4358, 0.5084, 0.5742, 0.641, 0.7114, 0.7924, 1.};

// mu mva 0.05 // FIXME missing rebinned
//TString sample = "mu_cos_theta_mva_0_05";
//Double_t list_x[bin_x+1] = {-1., -0.2248, 0., 0.2258, 0.387, 0.5388, 0.6898, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.424, -0.1804, 0., 0.0898, 0.1898, 0.2766, 0.3572, 0.4354, 0.5078, 0.574, 0.64, 0.7102, 0.7908, 1. };

// mu mva 0.09
//TString sample = "mu_cos_theta_mva_0_09";
//Double_t list_x[bin_x+1] = {-1., -0.2276, 0., 0.226, 0.3866, 0.5376, 0.6888, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.4216, -0.1806, 0., 0.0894, 0.1894, 0.2758, 0.3562, 0.4344, 0.507, 0.5736, 0.6394, 0.7092, 0.7894, 1. };

// mu mva 0.13
//TString sample = "mu_cos_theta_mva_0_13";
//Double_t list_x[bin_x+1] = {-1., -0.225, 0., 0.2252, 0.3858, 0.537, 0.6872, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.4162, -0.1774, 0., 0.0906, 0.1898, 0.2756, 0.3558, 0.4326, 0.5056, 0.5726, 0.6374, 0.7076, 0.7874, 1. };

// mu mva 0.17
//TString sample = "mu_cos_theta_mva_0_17";
//Double_t list_x[bin_x+1] = {-1., -0.2248, 0., 0.2234, 0.3838, 0.5342, 0.6852, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.416, -0.1768, 0., 0.09, 0.1898, 0.2752, 0.3556, 0.4322, 0.5052, 0.5714, 0.6358, 0.7058, 0.7864, 1. };

// ele mva 0.13
//TString sample = "ele_cos_theta_mva_0_13";
//Double_t list_x[bin_x+1] = {-1., -0.2732, 0., 0.2082, 0.3668, 0.519, 0.661, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.5204, -0.2444, 0., 0.0624, 0.1626, 0.2498, 0.3284, 0.4052, 0.4758, 0.5376, 0.6032, 0.6694, 0.7504, 1. }; 

// FIXME use this
// ele mva -0.03
TString sample = "ele_cos_theta_mva_-0_03";
Double_t list_x[bin_x+1] = {-1., -0.2818, 0., 0.2002, 0.3616, 0.516, 0.6606, 1. };
Double_t list_y[bin_y+1] = {-1., -0.5296, -0.2546, -0.0816, 0., 0.1518, 0.2402, 0.3212, 0.3996, 0.471, 0.535, 0.602, 0.6686, 0.753, 1. };

// mu_cos_theta
//TString sample = "mu_cos_theta";
//Double_t list_x[bin_x+1] = {-1., -0.2632, 0., 0.19, 0.3528, 0.5062, 0.6652, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.4496, -0.2254, 0., 0.048, 0.1478, 0.2346, 0.3174, 0.3956, 0.4738, 0.545, 0.6112, 0.6866, 0.7714, 1. };

// ele_cos_theta
//TString sample = "ele_cos_theta";
//Double_t list_x[bin_x+1] = {-1., -0.2856, 0., 0.1872, 0.3464, 0.4914, 0.6422, 1. };
//Double_t list_y[bin_y+1] = {-1., -0.5212, -0.2626, -0.0984, 0., 0.1298, 0.2154, 0.2954, 0.3726, 0.4428, 0.5096, 0.5728, 0.6432, 0.7298, 1. };

#endif
