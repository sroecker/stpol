#include "DataFormats/FWLite/interface/Event.h"

#ifndef CUTS_BASE_H
#define CUTS_BASE_H

#include <climits>
#include <TMath.h>

class BranchVars {
public:
    std::map<std::string, int> vars_int;
    std::map<std::string, float> vars_float;
    std::map<std::string, std::vector<float>> vars_vfloat;

    //the default values for TTree entries
    static const float def_val;
    static const int def_val_int;

};

//Base class for all work that is done inside the loop
class CutsBase {
public:

    //Map of the branch variables
    BranchVars& branch_vars;

    //Counter for the number of processed events
    unsigned long n_processed;

    //Counter for the number of events passing this Cut
    unsigned long n_pass;

    //Abstract method that sets the branch variables to sensible defaults on each loop
    virtual void initialize_branches() = 0;

    //Actually processes the event, loading the variables form the edm::EventBase into the branches
    virtual bool process(const edm::EventBase& event) = 0;
    
    std::string toString();

    CutsBase(BranchVars& _branch_vars);

    void pre_process();
    void post_process();
};

#endif
