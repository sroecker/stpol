#include "b_efficiency_calc.h"
#include <limits>
#include <cmath>

const float eps = std::numeric_limits<float>::epsilon();
bool AreSame(float a, float b) {
        return std::fabs(a - b) < eps;
}

const unsigned int eta_bins = 500;
const float eta_low = -5;
const float eta_high = 5;
const unsigned int pt_bins = 500;
const float pt_low = 0;
const float pt_high = 300;

const static std::vector<float> empty_vec;
void BEffCalcs::initialize_branches() {
}

BEffCalcs::BEffCalcs(const edm::ParameterSet& pars, BranchVars& _branch_vars, TFileDirectory& dir)
: CutsBase(_branch_vars)
, jet_pt_src(pars.getParameter<edm::InputTag>("jetPtSrc"))
, jet_eta_src(pars.getParameter<edm::InputTag>("jetEtaSrc"))
, jet_bdisc_src(pars.getParameter<edm::InputTag>("jetBDiscriminatorSrc"))
, jet_flavour_src(pars.getParameter<edm::InputTag>("jetFlavourSrc"))
, b_discriminator_wp(3.41)
{
    true_b_distribution = dir.make<TH2D>("true_b", "True b", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high); 
    true_b_tagged_distribution = dir.make<TH2D>("true_b_tagged", "True b tagged", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high); 
    
    true_c_distribution = dir.make<TH2D>("true_c", "True c", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high);
    true_c_tagged_distribution = dir.make<TH2D>("true_c_tagged", "True c tagged", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high); 
    
    true_l_distribution = dir.make<TH2D>("true_l", "True l", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high);
    true_l_tagged_distribution = dir.make<TH2D>("true_l_tagged", "True l tagged", eta_bins, eta_low, eta_high, pt_bins, pt_low, pt_high); 
}

bool BEffCalcs::process(const edm::EventBase& event) {
    pre_process();

    std::vector<float> jet_pts = get_collection<std::vector<float>>(event, jet_pt_src, empty_vec);
    std::vector<float> jet_etas = get_collection<std::vector<float>>(event, jet_eta_src, empty_vec);
    std::vector<float> jet_bdiscs = get_collection<std::vector<float>>(event, jet_bdisc_src, empty_vec);
    std::vector<float> jet_flavours = get_collection<std::vector<float>>(event, jet_flavour_src, empty_vec);
    const unsigned int size = jet_pts.size();
    if(jet_etas.size() != size || jet_bdiscs.size() != size || jet_flavours.size() != size) {
        throw;
    }

    for (unsigned int i=0; i<size; i++) {
        float pt = jet_pts[i]; 
        float eta = jet_etas[i]; 
        float bdisc = jet_bdiscs[i]; 
        float flavour = jet_flavours[i];

        TH2D* true_distr = 0;
        TH2D* true_tagged_distr = 0;

        //b
        if(AreSame(std::fabs(flavour), 5.0)) {
            true_distr = true_b_distribution; 
            true_tagged_distr = true_b_tagged_distribution; 
        }
        //c
        else if(AreSame(std::fabs(flavour), 4.0)) {
            true_distr = true_c_distribution; 
            true_tagged_distr = true_c_tagged_distribution; 
        }
        //l
        else {
            true_distr = true_l_distribution; 
            true_tagged_distr = true_l_tagged_distribution; 
        }

        if (bdisc >= b_discriminator_wp) {
            true_tagged_distr->Fill(eta, pt); 
        } else {
            true_distr->Fill(eta, pt); 
        }
    }
    post_process();
    return true;
}
