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

// 7 14

//Double_t list_x[bin_x+1] = {-1, -0.2778, -0.0162, 0.176, 0.3414, 0.4964, 0.6572, 1};
//Double_t list_y[bin_y+1] = {-1, -0.4674, -0.2558, -0.1028, 0.019, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1};

// 7 14 zero
//Double_t list_x[bin_x+1] = {-1, -0.2778, 0.0, 0.176, 0.3414, 0.4964, 0.6572, 1};
//Double_t list_y[bin_y+1] = {-1, -0.4674, -0.2558, -0.1028, 0.0, 0.116, 0.2126, 0.2956, 0.379, 0.4568, 0.5302, 0.6038, 0.6822, 0.7694, 1};

// 7 14 Andres zero

//Double_t list_x[bin_x+1] = {-1., -0.263, 0., 0.1896, 0.3526, 0.5062, 0.6654, 1.};
//Double_t list_y[bin_y+1] = {-1., -0.4496, -0.2254, -0.069, 0., 0.1476, 0.2346, 0.3174, 0.3956, 0.4738, 0.545, 0.6112, 0.6866, 0.7716 , 1. };

// new
//{-1, -0.2556, 0, 0.1982, 0.3602, 0.5144, 0.6738, 1};
//{-1, -0.4426, -0.2196, -0.0624, 0.055, 0.155, 0.2436, 0.327, 0.4028, 0.4812, 0.5516, 0.6196, 0.694, 0.7794, 1};

// 7 14 new zero
//Double_t list_x[bin_x+1] = {-1, -0.2556, 0, 0.1982, 0.3602, 0.5144, 0.6738, 1};
//Double_t list_y[bin_y+1] = {-1, -0.4426, -0.2196, -0.0624, 0, 0.155, 0.2436, 0.327, 0.4028, 0.4812, 0.5516, 0.6196, 0.694, 0.7794, 1};

Double_t list_x[bin_x+1] = {-1, -0.2632, 0, 0.19, 0.3528, 0.5062, 0.6652, 1};
Double_t list_y[bin_y+1] = {-1, -0.4496, -0.2254, -0.069, 0.0, 0.1478, 0.2346, 0.3174, 0.3956, 0.4738, 0.545, 0.6112, 0.6866, 0.7714, 1};

#endif
