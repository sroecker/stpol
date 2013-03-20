#include <TH1F.h>
#include <TTree.h>
#include <TROOT.h>
#include <TFile.h>
#include <TSystem.h>

#include "DataFormats/FWLite/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"

#include "DataFormats/MuonReco/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "FWCore/ParameterSet/interface/ProcessDesc.h"
#include "FWCore/PythonParameterSet/interface/PythonProcessDesc.h"

class HistoCut {
public:
    TH1F* hist;
    std::string cutname; 
    edm::InputTag var; 

    HistoCut(std::string name, int n_bins, float bins_low, float bins_high, std::string _cutname, edm::InputTag& _var) :
        hist(new TH1F(name.c_str(), name.c_str(), n_bins, bins_low, bins_high)),
        cutname(_cutname),
        var(_var)
    {
    }

    ~HistoCut() {
        delete hist;
    }

    virtual void Fill(edm::EventBase const & event) {
        std::cout << "Calling HistoCut::Fill" << std::endl;
        edm::Handle<float> handle;
        event.getByLabel(var, handle);
        hist->Fill((float)(*handle));
    }
};

class HistoCutV : public HistoCut {
public:
    const int vec_index;
    HistoCutV(std::string name, int n_bins, float bins_low, float bins_high, std::string _cutname, edm::InputTag& _var, int index) :
    HistoCut(name, n_bins, bins_low, bins_high, _cutname, _var),
    vec_index(index) 
    {
    }

    virtual void Fill(edm::EventBase const & event) {
        std::cout << "Calling HistoCutV::Fill" << std::endl;
        edm::Handle<std::vector<float> > handle;
        event.getByLabel(var, handle);
        if (vec_index<0) {
            for (auto& elem : *handle)
                hist->Fill(elem); 
        }
        else if (vec_index>0 && (unsigned int)vec_index<handle->size()) {
            hist->Fill(handle->at(vec_index));
        } else {
            hist->Fill(TMath::QuietNaN());
        }
    }
};

template <typename T>
T get_collection(const edm::EventBase& evt, edm::InputTag src, const T& retval) {
    edm::Handle<T> coll;
    evt.getByLabel(src, coll);
    if(!coll.isValid()) {
        return retval;
    }
    return *coll;
}

template <typename T>
float get_collection_n(const edm::EventBase& evt, edm::InputTag src, unsigned int n) {
    edm::Handle<std::vector<T>> coll;
    evt.getByLabel(src, coll);
    if(!(coll.isValid()) || n >= coll->size()) {
        return TMath::QuietNaN(); 
    }
    return (float)(coll->at(n));
}

template <typename F>
void check_cut(const std::string cutname, std::map<std::string, bool>& cut_map, std::map<std::string, int>& cut_count_map, F check) {
    bool passes = check();
    cut_map[cutname] = passes;
    if(passes) {
        cut_count_map[cutname] += 1;
    }
}

void fill_histos(const edm::EventBase& evt, const std::string cutname, std::map<std::string, std::vector<std::unique_ptr<HistoCut>>> histos) {
    if (histos.find(cutname) != histos.end()) {
        //for(std::unique_ptr<HistoCut> h : histos[cutname]) {
        //    h->Fill(evt);
        //}
    }
}

//class Cut {
//    
//}
//
//template <typename val_type>
//class CutVal : public Cut {
//    const edm::InputTag src;
//    CutVal(edm::InputTag _src, ) :
//    src(_src)
//    {
//    }
//
//}

class Muons {
public:
    bool reverseIsoCut;
    bool cutOnMuon;
    float muonPt;
    float isoVal;
    edm::InputTag muons_pt_src;
    edm::InputTag muons_reliso_src;
    float muon_pt(const edm::EventBase& event) {
        
    }
};

class 

void initialize_branches(std::map<std::string, float>& branch_vars) {
    branch_vars["top_mass"] = TMath::QuietNaN();
    branch_vars["cos_theta"] = TMath::QuietNaN();
    
    branch_vars["eta_lj"] = TMath::QuietNaN();
    branch_vars["pt_lj"] = TMath::QuietNaN();
    branch_vars["bdiscr_lj"] = TMath::QuietNaN();

    branch_vars["eta_bj"] = TMath::QuietNaN();
    branch_vars["pt_bj"] = TMath::QuietNaN();
    branch_vars["bdiscr_bj"] = TMath::QuietNaN();
    
    branch_vars["n_jets"] = TMath::QuietNaN();
    branch_vars["n_tags"] = TMath::QuietNaN();
    
    
    branch_vars["b_weight"] = TMath::QuietNaN();
}

int main(int argc, char* argv[])
{
    using pat::Muon;

    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();

    if ( argc < 2 ) {
        std::cout << "Usage : " << argv[0] << " [parameters.py]" << std::endl;
        return 0;
    }

    PythonProcessDesc builder(argv[1]);
    const edm::ParameterSet& in  = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("fwliteInput" );
    const edm::ParameterSet& out = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("fwliteOutput");
    const edm::ParameterSet& ana = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("muonAnalyzer");
    
    const edm::ParameterSet& mu_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("muonCuts");
    const edm::ParameterSet& ele_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("eleCuts");
    const edm::ParameterSet& jet_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("jetCuts");
    const edm::ParameterSet& final_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("finalCuts");
    const edm::ParameterSet& vars_to_save = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("varsToSave");

    std::string outputFile_( out.getParameter<std::string>("fileName" ) );
    std::vector<std::string> inputFiles_( in.getParameter<std::vector<std::string> >("fileNames") );

    MuonCuts muon_cuts;
    muon_cuts.cutOnMuon = mu_cuts_pars.getParameter<bool>("cutOnMuon");
    muon_cuts.reverseIsoCut = mu_cuts_pars.getParameter<bool>("reverseIsoCut");
    muon_cuts.muonPt = (float)mu_cuts_pars.getParameter<double>("muonPt");
    muon_cuts.isoVal = (float)mu_cuts_pars.getParameter<double>("isoVal");
    fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());

    // now get each parameter
    int maxEvents_( in.getParameter<int>("maxEvents") );
    unsigned int outputEvery_( in.getParameter<unsigned int>("outputEvery") );

    TFileDirectory dir = fs.mkdir("trees");
    TTree outTree("Events", "Events");
    
    std::map<std::string, float> branch_vars;
    initialize_branches(branch_vars);
    
    outTree.Branch("top_mass", &branch_vars["top_mass"]);
    outTree.Branch("cos_theta", &branch_vars["cos_theta"]);
    
    outTree.Branch("eta_lj", &branch_vars["eta_lj"]);
    outTree.Branch("pt_lj", &branch_vars["pt_lj"]);
    outTree.Branch("bdiscr_lj", &branch_vars["bdiscr_lj"]);
    
    outTree.Branch("eta_bj", &branch_vars["eta_bj"]);
    outTree.Branch("pt_bj", &branch_vars["pt_bj"]);
    outTree.Branch("bdiscr_bj", &branch_vars["bdiscr_bj"]);
    
    outTree.Branch("n_jets", &branch_vars["n_jets"]);
    outTree.Branch("n_tags", &branch_vars["n_tags"]);
    
    outTree.Branch("b_weight", &branch_vars["b_weight"]);

    // loop the events
    int ievt=0;

    for(unsigned int iFile=0; iFile<inputFiles_.size(); ++iFile) {
        // open input file (can be located on castor)
        TFile* inFile = TFile::Open(inputFiles_[iFile].c_str());
        if( inFile ) {
            
            fwlite::Event ev(inFile);
            for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt) {
                edm::EventBase const & event = ev;
                initialize_branches(branch_vars);
                
                // break loop if maximal number of events is reached
                if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
                
                if(outputEvery_!=0 ? (ievt>0 && ievt%outputEvery_==0) : false)
                    std::cout << "  processing event: " << ievt << std::endl;

                

                outTree.Fill();
            }
            inFile->Close();
        }
        // break loop if maximal number of events is reached:
        // this has to be done twice to stop the file loop as well
        if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
    }
//    for (auto& elem : cut_count_map) {
//        std::cout << elem.first << " " << elem.second << std::endl;
//    }

    return 0;
}
