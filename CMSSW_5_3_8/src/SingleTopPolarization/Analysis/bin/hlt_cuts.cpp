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
    
    //std::cout << trig_names.size() << std::endl;
    //for(unsigned int i=0;i<trig_names.size(); i++) {
    //    std::cout << trig_names.triggerName(i) << " "; 
    //}
    //std::cout << std::endl;
    //Tabulate specified HLT-s
    for(auto & name : hlt_names) {
        //std::cout << "index=" << trig_names.triggerIndex(name) << std::endl;
        unsigned int idx = trig_names.triggerIndex(name);
        if(idx>=trig_results->size()) {
            //std::cerr << "Could not find trigger " << name << " idx=" << idx << std::endl; 
            branch_vars[name] = -1;
        }
        else {
            branch_vars[name] = (int)trig_results->accept(idx);
        } 
        //std::cout << branch_vars[name] << std::endl; 
    }

    //Cut on one specific HLT
    if(cut_on_HLT) {
        unsigned int idx = trig_names.triggerIndex(hlt_cut_name);
        if(idx>=trig_results->size()) {
            //std::cerr << "Could not find trigger " << name << " idx=" << idx << std::endl; 
            branch_vars[hlt_cut_name] = -1;
        }
        else {
            branch_vars[hlt_cut_name] = (int)trig_results->accept(idx);
        }
        if (branch_vars[hlt_cut_name] != 1) return false;
    }

    post_process();
    return true;
}
