#include "hlt_cuts.h"

void HLTCuts::initialize_branches() {
    for(auto & name : hlt_names) {
        branch_vars.vars_int[name] = BranchVars::def_val_int; 
    }
}

HLTCuts::HLTCuts(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
CutsBase(_branch_vars)
{
    hlt_src = pars.getParameter<edm::InputTag>("hltSrc");
    hlt_names = pars.getParameter<std::vector<std::string> >("hltNames");
    cut_on_HLT = pars.getParameter<bool>("doCutOnHLT");
    initialize_branches();
}

bool HLTCuts::process(const edm::EventBase& event) {
    pre_process();
    
    event.getByLabel(hlt_src, trig_results);
    const edm::TriggerNames& trig_names = event.triggerNames(*trig_results);
    
    //Tabulate specified HLT-s
    bool passes = false;
    for(auto & name : hlt_names) {
        unsigned int idx = trig_names.triggerIndex(name);
   
        //trigger was not found
        if(idx >= trig_results->size()) {
            branch_vars.vars_int[name] = BranchVars::def_val_int;
        }
        else {
            branch_vars.vars_int[name] = (int)trig_results->accept(idx);
            
            //Triggers in list are applied with OR
            passes = passes || trig_results->accept(idx);
        } 
    }

    if (cut_on_HLT && !passes) return false;

    post_process();
    return true;
}
