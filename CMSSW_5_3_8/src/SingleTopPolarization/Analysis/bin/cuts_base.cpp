#include "cuts_base.h"

template <typename T>
CutsBase<T>::CutsBase(std::map<std::string, T>& _branch_vars) :
branch_vars(_branch_vars)
{
    //initialize_branches(); //Can't call virtual method form constructor
    n_processed = 0;
    n_pass = 0;
}

template <typename T>
std::string CutsBase<T>::toString() {
    std::stringstream ss;
    ss << "Processed: " << n_processed << " Passed: " << n_pass;
    return ss.str();
}

template <typename T>
void CutsBase<T>::pre_process() {
    initialize_branches();
    n_processed += 1;
}

template <typename T>
void CutsBase<T>::post_process() {
    n_pass += 1;
}

template class CutsBase<float>;
template class CutsBase<int>;
