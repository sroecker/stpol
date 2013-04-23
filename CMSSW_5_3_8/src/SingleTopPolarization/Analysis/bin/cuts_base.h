#include "DataFormats/FWLite/interface/Event.h"

//Base class for all work that is done inside the loop
class CutsBase {
public:

    //Map of the branch variables
    std::map<std::string, float>& branch_vars;

    //Counter for the number of processed events
    unsigned long n_processed;

    //Counter for the number of events passing this Cut
    unsigned long n_pass;

    //Abstract method that sets the branch variables to sensible defaults on each loop
    virtual void initialize_branches() = 0;

    //Actually processes the event, loading the variables form the edm::EventBase into the branches
    virtual bool process(const edm::EventBase& event) = 0;
    
    std::string toString();

    CutsBase(std::map<std::string, float>& _branch_vars);

    void pre_process();
    void post_process();
};
