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

static const float def_val = (const float)(TMath::QuietNaN());

class CutsBase {
public:
    std::map<std::string, float>& branch_vars;
    unsigned long n_processed;
    unsigned long n_pass;
    virtual void initialize_branches() = 0;
    virtual bool process(const edm::EventBase& event) = 0;
    CutsBase(std::map<std::string, float>& _branch_vars) :
    branch_vars(_branch_vars)
    {
        //initialize_branches();
        n_processed = 0;
        n_pass = 0;
    }
    
    std::string toString() {
        std::stringstream ss;
        ss << "Processed: " << n_processed << " Passed: " << n_pass;
        return ss.str();
    }
    
    void pre_process() {
        initialize_branches();
        n_processed += 1;
    }
    
    void post_process() {
        n_pass += 1;
    }
};

class MuonCuts : public CutsBase {
public:
    bool cutOnIso;
    bool reverseIsoCut;
    
    float isoCut;
    edm::InputTag muonPtSrc;
    edm::InputTag muonRelIsoSrc;
    
    virtual void initialize_branches() {
        branch_vars["mu_pt"] = def_val;
        branch_vars["mu_iso"] = def_val;
    }
    
    MuonCuts(const edm::ParameterSet& pars, std::map< std::string, float> & _branch_vars) :
    CutsBase(_branch_vars)
    {
        initialize_branches();
        cutOnIso = pars.getParameter<bool>("cutOnIso");
        reverseIsoCut = pars.getParameter<bool>("reverseIsoCut");
        isoCut = (float)pars.getParameter<double>("isoCut");
        
        muonPtSrc = pars.getParameter<edm::InputTag>("muonPtSrc");
        muonRelIsoSrc = pars.getParameter<edm::InputTag>("muonRelIsoSrc");
        
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["mu_pt"] = get_collection_n<float>(event, muonPtSrc, 0);
        branch_vars["mu_iso"] = get_collection_n<float>(event, muonRelIsoSrc, 0);
        bool passesMuIso = true;
        if (cutOnIso) {
            if(!reverseIsoCut)
                passesMuIso = branch_vars["mu_iso"] < isoCut;
            else
                passesMuIso = branch_vars["mu_iso"] > isoCut;
        }
        if(cutOnIso && !passesMuIso) return false;
        
        post_process();
        return true;
    }
};

class JetCuts : public CutsBase {
public:
    bool cutOnNJets;
    bool cutOnNTags;
    
    bool applyRmsLj;
    float rmsMax;
    
    int nJetsCutMax;
    int nJetsCutMin;
    int nTagsCutMin;
    int nTagsCutMax;
    
    bool applyEtaLj;
    
    edm::InputTag goodJetsCountSrc;
    edm::InputTag bTagJetsCountSrc;
    
    edm::InputTag goodJetsPtSrc;
    edm::InputTag goodJetsEtaSrc;
    
    edm::InputTag lightJetEtaSrc;
    edm::InputTag lightJetBdiscrSrc;
    edm::InputTag lightJetPtSrc;
    edm::InputTag lightJetRmsSrc;
    
    edm::InputTag bJetEtaSrc;
    edm::InputTag bJetBdiscrSrc;
    edm::InputTag bJetPtSrc;
    
    virtual void initialize_branches() {
        branch_vars["pt_lj"] = def_val;
        branch_vars["eta_lj"] = def_val;
        branch_vars["bdiscr_lj"] = def_val;
        branch_vars["rms_lj"] = def_val;
        
        branch_vars["pt_bj"] = def_val;
        branch_vars["eta_bj"] = def_val;
        branch_vars["bdiscr_bj"] = def_val;
        
        branch_vars["n_jets"] = def_val;
        branch_vars["n_tags"] = def_val;
    }
    
    JetCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBase(_branch_vars)
    {
        cutOnNJets =  pars.getParameter<bool>("cutOnNJets");
        cutOnNTags =  pars.getParameter<bool>("cutOnNTags");
        applyRmsLj =  pars.getParameter<bool>("applyRmsLj");
        applyEtaLj =  pars.getParameter<bool>("applyEtaLj");
        
        rmsMax = pars.getParameter<double>("rmsMax");
        
        nJetsCutMax = pars.getParameter<int>("nJetsMax");
        nJetsCutMin = pars.getParameter<int>("nJetsMin");
        nTagsCutMax = pars.getParameter<int>("nTagsMax");
        nTagsCutMin = pars.getParameter<int>("nTagsMin");
        
        goodJetsCountSrc = pars.getParameter<edm::InputTag>("goodJetsCountSrc");
        bTagJetsCountSrc = pars.getParameter<edm::InputTag>("bTagJetsCountSrc");
        
        goodJetsPtSrc = pars.getParameter<edm::InputTag>("goodJetsPtSrc");
        goodJetsEtaSrc = pars.getParameter<edm::InputTag>("goodJetsEtaSrc");
        
        lightJetEtaSrc = pars.getParameter<edm::InputTag>("lightJetEtaSrc");
        lightJetBdiscrSrc = pars.getParameter<edm::InputTag>("lightJetBdiscrSrc");
        lightJetPtSrc = pars.getParameter<edm::InputTag>("lightJetPtSrc");
        lightJetRmsSrc = pars.getParameter<edm::InputTag>("lightJetRmsSrc");
        
        bJetEtaSrc = pars.getParameter<edm::InputTag>("bJetEtaSrc");
        bJetBdiscrSrc = pars.getParameter<edm::InputTag>("bJetBdiscrSrc");
        bJetPtSrc = pars.getParameter<edm::InputTag>("bJetPtSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        branch_vars["pt_lj"] = get_collection_n<float>(event, lightJetPtSrc, 0);
        branch_vars["eta_lj"] = get_collection_n<float>(event, lightJetEtaSrc, 0);
        branch_vars["bdiscr_lj"] = get_collection_n<float>(event, lightJetBdiscrSrc, 0);
        branch_vars["rms_lj"] = get_collection_n<float>(event, lightJetRmsSrc, 0);
        bool passes_rms_lj = (branch_vars["rms_lj"] < rmsMax);
        
        branch_vars["pt_bj"] = get_collection_n<float>(event, bJetPtSrc, 0);
        branch_vars["eta_bj"] = get_collection_n<float>(event, bJetEtaSrc, 0);
        branch_vars["bdiscr_bj"] = get_collection_n<float>(event, bJetBdiscrSrc, 0);
        branch_vars["n_jets"] = get_collection<int>(event, goodJetsCountSrc, -1);
        branch_vars["n_tags"] = get_collection<int>(event, bTagJetsCountSrc, -1);
        
        if (cutOnNJets && branch_vars["n_jets"] <= nJetsCutMax && branch_vars["n_jets"] >= nJetsCutMin) return false;
        if (cutOnNTags && branch_vars["n_tags"] <= nTagsCutMax && branch_vars["n_tags"] >= nTagsCutMin) return false;
        if (applyRmsLj && !passes_rms_lj) return false;
        
        post_process();
        return true;
    }
};

class TopCuts : public CutsBase {
public:
    bool applyMassCut;
    bool signalRegion;
    float signalRegionMassLow;
    float signalRegionMassHigh;
    edm::InputTag topMassSrc;
    
    virtual void initialize_branches() {
        branch_vars["top_mass"] = def_val;
    }
    
    TopCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBase(_branch_vars)
    {
        initialize_branches();
        applyMassCut = pars.getParameter<bool>("applyMassCut");
        signalRegion = pars.getParameter<bool>("signalRegion");
        signalRegionMassLow = (float)pars.getParameter<double>("signalRegionMassLow");
        signalRegionMassHigh = (float)pars.getParameter<double>("signalRegionMassHigh");
        
        topMassSrc = pars.getParameter<edm::InputTag>("topMassSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["top_mass"] = get_collection_n<float>(event, topMassSrc, 0);
        bool passes_mass_cut = true;
        if(applyMassCut) {
            if(signalRegion) {
                passes_mass_cut = (branch_vars["top_mass"] < signalRegionMassHigh) && (branch_vars["top_mass"] > signalRegionMassLow);
            } else {
                //sideband region
                passes_mass_cut = (branch_vars["top_mass"] > signalRegionMassHigh) || (branch_vars["top_mass"] < signalRegionMassLow);
            }
        }
        
        if(!passes_mass_cut) return false;
        
        post_process();
        return true;
    }
};

class BWeightCuts : public CutsBase {
public:
    edm::InputTag bWeightNominalSrc;
    
    void initialize_branches() {
        branch_vars["b_weight_nominal"] = def_val;
    }
    
    BWeightCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBase(_branch_vars)
    {
        bWeightNominalSrc = pars.getParameter<edm::InputTag>("bWeightNominalSrc");
        
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["b_weight_nominal"] = get_collection<double>(event, bWeightNominalSrc, def_val);
        
        post_process();
        return true;
    }
};

class MTMuCuts : public CutsBase {
public:
    edm::InputTag mtMuSrc;
    float minVal;
    
    void initialize_branches() {
        branch_vars["mt_mu"] = def_val;
    }
    
    MTMuCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBase(_branch_vars)
    {
        mtMuSrc = pars.getParameter<edm::InputTag>("mtMuSrc");
        minVal = (float)pars.getParameter<double>("minVal");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["mt_mu"] = get_collection<double>(event, mtMuSrc, def_val);
        
        post_process();
        return true;
    }
};

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
    
    std::string outputFile_( out.getParameter<std::string>("fileName" ) );
    std::vector<std::string> inputFiles_( in.getParameter<std::vector<std::string> >("fileNames") );
    
    const edm::ParameterSet& mu_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("muonCuts");
    const edm::ParameterSet& ele_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("eleCuts");
    const edm::ParameterSet& jet_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("jetCuts");
    const edm::ParameterSet& top_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("topCuts");
    const edm::ParameterSet& mt_mu_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("mtMuCuts");
    const edm::ParameterSet& bweight_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("bWeights");
    const edm::ParameterSet& costheta_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("cosTheta");
    
    //const edm::ParameterSet& vars_to_save = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("varsToSave");
    
    std::map<std::string, float> branch_vars;
    
    MuonCuts muon_cuts(mu_cuts_pars, branch_vars);
    JetCuts jet_cuts(jet_cuts_pars, branch_vars);
    TopCuts top_cuts(top_cuts_pars, branch_vars);
    BWeightCuts bweights(bweight_pars, branch_vars);
    MTMuCuts mt_mu_cuts(mt_mu_cuts_pars, branch_vars);
    
    fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());
    
    // now get each parameter
    int maxEvents_( in.getParameter<int>("maxEvents") );
    unsigned int outputEvery_( in.getParameter<unsigned int>("outputEvery") );
    
    TFileDirectory dir = fs.mkdir("trees");
    TTree* outTree = dir.make<TTree>("Events", "Events");
    //dir.cd();
    
    //Create all the requested branches in the TTree
    for (auto & elem : branch_vars) {
        const std::string& br_name = elem.first;
        float* p_branch = &(elem.second);
        outTree->Branch(br_name.c_str(), p_branch);
    }
    
    // loop the events
    int ievt=0;
    for(unsigned int iFile=0; iFile<inputFiles_.size(); ++iFile) {
        // open input file (can be located on castor)
        TFile* inFile = TFile::Open(inputFiles_[iFile].c_str());
        if( inFile ) {
            
            fwlite::Event ev(inFile);
            for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt) {
                edm::EventBase const & event = ev;
                
                muon_cuts.initialize_branches();
                jet_cuts.initialize_branches();
                // break loop if maximal number of events is reached
                if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
                
                if(outputEvery_!=0 ? (ievt>0 && ievt%outputEvery_==0) : false)
                    std::cout << "  processing event: " << ievt << std::endl;
                
                bool passes_muon_cuts = muon_cuts.process(event);
                if(!passes_muon_cuts) continue;
                
                bool passes_mt_mu_cuts = mt_mu_cuts.process(event);
                if(!passes_mt_mu_cuts) continue;
                
                bool passes_jet_cuts = jet_cuts.process(event);
                if(!passes_jet_cuts) continue;
                
                bool passes_top_cuts = top_cuts.process(event);
                if(!passes_top_cuts) continue;
                
                bweights.process(event);
                
                outTree->Fill();
            }
            inFile->Close();
        }
        // break loop if maximal number of events is reached:
        // this has to be done twice to stop the file loop as well
        //if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
    }
    
    std::cout << "muon cuts " << muon_cuts.toString() << std::endl;
    std::cout << "mt_mu cuts " << mt_mu_cuts.toString() << std::endl;
    std::cout << "jet cuts " << jet_cuts.toString() << std::endl;
    std::cout << "top cuts " << top_cuts.toString() << std::endl;
    
    
    //    for (auto& elem : cut_count_map) {
    //        std::cout << elem.first << " " << elem.second << std::endl;
    //    }
    
    return 0;
}
