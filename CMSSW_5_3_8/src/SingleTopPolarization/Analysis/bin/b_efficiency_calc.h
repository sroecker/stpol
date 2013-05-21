#include "cuts_base.h"
#include "TFile.h"
#ifndef B_EFF_CALC_H
#define B_EFF_CALC_H


class BEffCalcs : public CutsBase {
public:
    edm::InputTag jet_pt_src;
    edm::InputTag jet_eta_src;
    edm::InputTag jet_bdisc_src;
    edm::InputTag jet_flavour_src;
    void initialize_branches();
    TFile& file;

    BEffCalcs(const edm::ParameterSet& pars, BranchVars& _branch_vars, TFile& _file);

    bool process(const edm::EventBase& event);
};
#endif
