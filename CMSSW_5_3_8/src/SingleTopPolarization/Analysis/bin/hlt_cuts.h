#include "cuts_base.h"
#include <DataFormats/Common/interface/TriggerResults.h>
#include <FWCore/ParameterSet/interface/ProcessDesc.h>
#include <FWCore/PythonParameterSet/interface/PythonProcessDesc.h>
#include <FWCore/PythonParameterSet/interface/PythonProcessDesc.h>
#include <FWCore/Common/interface/TriggerNames.h>
#ifndef HLT_CUTS_H
#define HLT_CUTS_H


class HLTCuts : public CutsBaseI {
public:
    edm::InputTag hlt_src;
    std::vector<std::string> hlt_names;
    bool cut_on_HLT;
    std::vector<std::string> hlt_cut_names;

    edm::Handle<edm::TriggerResults> trig_results;
    void initialize_branches();
     
    HLTCuts(const edm::ParameterSet& pars, std::map<std::string, int>& _branch_vars);

    bool process(const edm::EventBase& event);
};
#endif
