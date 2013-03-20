#include <TH1F.h>
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

    // now get each parameter
    int maxEvents_( in.getParameter<int>("maxEvents") );
    unsigned int outputEvery_( in.getParameter<unsigned int>("outputEvery") );

    std::string outputFile_( out.getParameter<std::string>("fileName" ) );
    std::vector<std::string> inputFiles_( in.getParameter<std::vector<std::string> >("fileNames") );
    edm::InputTag muon_iso_src( ana.getParameter<edm::InputTag>("muon_iso_src") );
    edm::InputTag mt_mu_src( ana.getParameter<edm::InputTag>("mt_mu_src") );
    edm::InputTag muon_count_src( ana.getParameter<edm::InputTag>("muon_count_src") );
    edm::InputTag veto_muon_count_src( ana.getParameter<edm::InputTag>("veto_muon_count_src") );
    edm::InputTag veto_ele_count_src( ana.getParameter<edm::InputTag>("veto_ele_count_src") );
    edm::InputTag mlnu_mass_src( ana.getParameter<edm::InputTag>("mlnu_mass_src") );
    edm::InputTag light_jet_eta_src( ana.getParameter<edm::InputTag>("light_jet_eta_src") );
    edm::InputTag light_jet_rms_src( ana.getParameter<edm::InputTag>("light_jet_rms_src") );
    edm::InputTag good_jet_count_src( ana.getParameter<edm::InputTag>("good_jet_count_src") );
    edm::InputTag btag_jet_count_src( ana.getParameter<edm::InputTag>("btag_jet_count_src") );

    // book a set of histograms
    fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());
    
    const std::vector<edm::ParameterSet> & histos = builder.processDesc()->getProcessPSet()->getParameter<std::vector<edm::ParameterSet> >("histos");
    TFileDirectory dir = fs.mkdir("histos");
    std::map<std::string, std::vector<std::unique_ptr<HistoCut>>> cut_histos;

    for (auto & histo_pset : histos) {
        
        std::string name = histo_pset.getParameter<std::string>("name"); 
        edm::InputTag var = histo_pset.getParameter<edm::InputTag>("var"); 
        std::string formula = histo_pset.getParameter<std::string>("formula"); 
        unsigned int n_bins = histo_pset.getParameter<unsigned int>("nbins"); 
        float bins_low = (float)histo_pset.getParameter<double>("binslow"); 
        float bins_high = (float)histo_pset.getParameter<double>("binshigh"); 

        std::string cutname = histo_pset.getParameter<std::string>("cutname");
        unsigned int srctype = histo_pset.getParameter<unsigned>("srctype");
        int vecindex = histo_pset.getParameter<int>("vecindex");

 
        TH1F* hist  = dir.make<TH1F>(name.c_str() ,name.c_str(), n_bins, bins_low, bins_high);
        if (cut_histos.find(cutname) != cut_histos.end()) {
        //    cut_histos[cutname] = std::vector<std::unique_ptr<HistoCut>>();
        } 
        //if (srctype==0)
        //    cut_histos[cutname].push_back(std::unique_ptr<HistoCut>( new HistoCut(name, n_bins, bins_low, bins_high, cutname, var))); 
        //else if (srctype==1)
        //    cut_histos[cutname].push_back(std::unique_ptr<HistoCut>( new HistoCutV(name, n_bins, bins_low, bins_high, cutname, var, vecindex))); 
        else
            throw "Error"; 
        //std::cout << "histo pset" << std::endl;
        //std::cout << "name=" << histo_pset.getParameter<std::string>("name") << std::endl;
        //std::cout << "var=" << histo_pset.getParameter<edm::InputTag>("var").encode() << std::endl;
        //std::cout << "formula=" << histo_pset.getParameter<std::string>("formula") << std::endl;
    } 

    float mu_iso_max = 0.12;
    float mt_mu_min = 50;
    //float jet_pt_min = 40;
    float eta_lj_min = 2.5;
    float rms_lj_max = 0.025;
    int n_tags_required = 1;
    int n_jets_required = 2;
 
    std::map<std::string, bool> cut_map;
    std::map<std::string, int> cut_count_map;


    // loop the events
    int ievt=0;

    for(unsigned int iFile=0; iFile<inputFiles_.size(); ++iFile) {
        // open input file (can be located on castor)
        TFile* inFile = TFile::Open(inputFiles_[iFile].c_str());
        if( inFile ) {
            
            fwlite::Event ev(inFile);
            for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt) {
                edm::EventBase const & event = ev;
                
                // break loop if maximal number of events is reached
                if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
                
                if(outputEvery_!=0 ? (ievt>0 && ievt%outputEvery_==0) : false)
                    std::cout << "  processing event: " << ievt << std::endl;

                //Cut on muon count
                int muon_count = get_collection<int>(event, muon_count_src, -1);               
                check_cut(std::string("has_mu"), cut_map, cut_count_map,
                    [&]() {
                        return muon_count > 0;
                    }
                );
                if (!cut_map["has_mu"]) continue;
                
                int veto_mu_count = get_collection<int>(event, veto_muon_count_src, -1);               
                check_cut(std::string("passes_veto_mu"), cut_map, cut_count_map,
                    [&]() {
                        return veto_mu_count == 0;
                    }
                );
                if (!cut_map["passes_veto_mu"]) continue;
                
                int veto_ele_count = get_collection<int>(event, veto_ele_count_src, -1);               
                check_cut(std::string("passes_veto_ele"), cut_map, cut_count_map,
                    [&]() {
                        return veto_ele_count == 0;
                    }
                );
                if (!cut_map["passes_veto_ele"]) continue;
               
                float muon_iso =  get_collection_n<float>(event, muon_iso_src, 0);
                check_cut(std::string("muon_iso"), cut_map, cut_count_map,
                    [&]() {
                        return muon_iso < mu_iso_max;
                    }
                );
                if (!cut_map["muon_iso"]) continue;
                
                float mt_mu = get_collection<double>(event, mt_mu_src, -1.0);
                check_cut(std::string("mt_mu"), cut_map, cut_count_map,
                    [&]() {
                        return mt_mu > mt_mu_min;
                    }
                );
                if (!cut_map["mt_mu"]) continue;
                
                fill_histos(event, "mt_mu", cut_histos); 
                float eta_lj = get_collection_n<float>(event, light_jet_eta_src, 0);
                check_cut(std::string("eta_lj"), cut_map, cut_count_map,
                    [&]() {
                        return fabs(eta_lj) > eta_lj_min;
                    }
                );
                if (!cut_map["eta_lj"]) continue;
                
                float rms_lj = get_collection_n<float>(event, light_jet_rms_src, 0);
                check_cut(std::string("rms_lj"), cut_map, cut_count_map,
                    [&]() {
                        return rms_lj < rms_lj_max;
                    }
                );
                if (!cut_map["rms_lj"]) continue;
                
                int jet_count = get_collection<int>(event, good_jet_count_src, 0);
                check_cut(std::string("n_jets"), cut_map, cut_count_map,
                    [&]() {
                        return jet_count==n_jets_required;
                    }
                );
                if (!cut_map["n_jets"]) continue;

                int btag_jet_count = get_collection<int>(event, btag_jet_count_src, 0);
                check_cut(std::string("n_tags"), cut_map, cut_count_map,
                    [&]() {
                        return btag_jet_count==n_tags_required;
                    }
                );
                if (!cut_map["n_tags"]) continue;
                
                //check_cut(event, mt_mu_src, std::string("mt_mu"), cut_map, cut_count_map,
                //    [&]() {
                //        float x = get_collection<int>(event, mt_mu_src, -1);
                //        return x>mt_mu_min;
                //    }
                //);
                //if (!cut_map["mt_mu"]) continue;
 
                //int muon_count = get_collection<int>(event, muon_count_src, 0); 
                //cut_map["has_muon"] = muon_count>0;
                //if(!cut_map["has_muon"]) continue;
                //cut_count_map["has_muon"] += 1;

                //float mu_pt = get_collection_n<float>(event, muon_pt_src, 0);
                //bool passes_mu_pt = mu_pt > mu_pt_min;
                //if(!passes_mu_pt) continue;
                //passes_mu_pt += 1;
                //
                //float mt_mu = get_collection_n<float>(event, mt_mu_src, 0);
                //bool passes_mt_mu = mt_mu > mt_mu_min;
                //if(!passes_mt_mu) continue;
                //passes_mt_mu += 1; 
            }
            // close input file
            inFile->Close();
        }
        // break loop if maximal number of events is reached:
        // this has to be done twice to stop the file loop as well
        if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
    }
    for (auto& elem : cut_count_map) {
        std::cout << elem.first << " " << elem.second << std::endl;
    }

    return 0;
}
