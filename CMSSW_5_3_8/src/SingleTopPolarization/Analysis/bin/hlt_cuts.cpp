#include "hlt_cuts.h"

void HLTCuts::initialize_branches() {
    for(auto & name : hlt_names) {
        branch_vars[name] = -1; 
    }
}

HLTCuts::HLTCuts(const edm::ParameterSet& pars, std::map<std::string, int>& _branch_vars) :
CutsBaseI(_branch_vars)
{
    hlt_src = pars.getParameter<edm::InputTag>("hltSrc");
    hlt_names = pars.getParameter<std::vector<std::string> >("hltNames");
    hlt_cut_name = pars.getParameter<std::string>("cutOnHLT");
    cut_on_HLT = pars.getParameter<bool>("doCutOnHLT");
    initialize_branches();
}

bool HLTCuts::process(const edm::EventBase& event) {
    pre_process();
    
    event.getByLabel(hlt_src, trig_results);
    const edm::TriggerNames& trig_names = event.triggerNames(*trig_results);
    
    //Tabulate specified HLT-s
    for(auto & name : hlt_names) {
        branch_vars[name] = (int)trig_results->accept(trig_names.triggerIndex(name));  
    }

    //Cut on one specific HLT
    if(cut_on_HLT) {
        trig_results->accept(trig_names.triggerIndex(hlt_cut_name));
    }

    post_process();
    return true;
}
