#include "cuts_base.h"

CutsBase::CutsBase(std::map<std::string, float>& _branch_vars) :
branch_vars(_branch_vars)
{
    //initialize_branches(); //Can't call virtual method form constructor
    n_processed = 0;
    n_pass = 0;
}

std::string CutsBase::toString() {
    std::stringstream ss;
    ss << "Processed: " << n_processed << " Passed: " << n_pass;
    return ss.str();
}

void CutsBase::pre_process() {
    initialize_branches();
    n_processed += 1;
}

void CutsBase::post_process() {
    n_pass += 1;
}
