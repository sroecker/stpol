#include <TH1F.h>
#include <TTree.h>
#include <TROOT.h>
#include <TFile.h>
#include <TSystem.h>
#include <TStopwatch.h>
#include <TMath.h>

#include "DataFormats/FWLite/interface/Event.h"
#include "DataFormats/Common/interface/Handle.h"
#include "FWCore/FWLite/interface/AutoLibraryLoader.h"

#include "DataFormats/MuonReco/interface/Muon.h"
//#include "DataFormats/PatCandidates/interface/Muon.h"
#include "PhysicsTools/FWLite/interface/TFileService.h"
#include "FWCore/ParameterSet/interface/ProcessDesc.h"
#include "FWCore/PythonParameterSet/interface/PythonProcessDesc.h"
#include "DataFormats/Common/interface/MergeableCounter.h"
#include "cuts_base.h"

#include <stdio.h>
#include <time.h>

// Get current date/time, format is YYYY-MM-DD.HH:mm:ss
const std::string currentDateTime() {
    time_t     now = time(0);
    struct tm  tstruct;
    char       buf[80];
    tstruct = *localtime(&now);
    // Visit http://www.cplusplus.com/reference/clibrary/ctime/strftime/
    // for more information about date/time format
    strftime(buf, sizeof(buf), "%Y-%m-%d.%X", &tstruct);

    return buf;
}
//A simple logging macro
#define LogInfo std::cout << currentDateTime() << ":"

using namespace std;

int get_parent(const std::string& decay_tree, int self_pdgid) {
    for(std::string::size_type i = 0; i < decay_tree.size(); ++i) {
        const char s = decay_tree[i];
        if (s == '(') {
            std::string::size_type j = decay_tree.find(":", i);
            const std::string subs = decay_tree.substr(i+1, j-i-1);
            std::istringstream ss(subs);
            int pdgid = 0;
            ss >> pdgid;
            if (pdgid == 0)
                std::cerr << "Couldn't understand parent: " << subs << " <= " << decay_tree << std::endl;
            //std::cout << subs << "->" << pdgid << std::endl;
            if (abs(pdgid) != self_pdgid) {
                //std::cout << "Identified " << pdgid << std::endl;
                return pdgid;
            }
        }
    }
    std::cerr << "Couldn't parse decay tree: " << decay_tree << std::endl;
    return 0;
}

//Shorthand for getting a value of type T from the event, where the original container is vector<T>
template <typename T>
float get_collection_n(const edm::EventBase& evt, edm::InputTag src, unsigned int n) {
    edm::Handle<std::vector<T>> coll;
    evt.getByLabel(src, coll);
    if(!(coll.isValid()) || n >= coll->size()) {
        return TMath::QuietNaN();
    }
    return (float)(coll->at(n));
}

const std::string default_str("");
class MuonCuts : public CutsBase {
public:
    edm::InputTag muonPtSrc;
    edm::InputTag muonRelIsoSrc;
    edm::InputTag muonCountSrc;
    edm::InputTag eleCountSrc;
    
    edm::InputTag muonDbSrc;
    edm::InputTag muonDzSrc;
    edm::InputTag muonNormChi2Src;
    edm::InputTag muonChargeSrc;
    
    edm::InputTag muonDecayTreeSrc;

    virtual void initialize_branches() {
        branch_vars.vars_float["mu_pt"] = BranchVars::def_val;
        branch_vars.vars_float["mu_iso"] = BranchVars::def_val;
        
        //branch_vars.vars_int["n_muons"] = BranchVars::def_val;
        //branch_vars.vars_int["n_eles"] = BranchVars::def_val;
        
        //branch_vars.vars_int["mu_charge"] = BranchVars::def_val_int;            
        branch_vars.vars_int["mu_mother_id"] = BranchVars::def_val_int;        
    }
    
    MuonCuts(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
    CutsBase(_branch_vars)
    {
        initialize_branches();
        muonPtSrc = pars.getParameter<edm::InputTag>("muonPtSrc");
        muonRelIsoSrc = pars.getParameter<edm::InputTag>("muonRelIsoSrc");
        
        //muonChargeSrc = pars.getParameter<edm::InputTag>("muonChargeSrc");

        muonDecayTreeSrc = pars.getParameter<edm::InputTag>("muonDecayTreeSrc");
        
        //muonCountSrc = pars.getParameter<edm::InputTag>("muonCountSrc"); 
        //eleCountSrc = pars.getParameter<edm::InputTag>("eleCountSrc"); 
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        /*int n_muons = get_collection<int>(event, muonCountSrc, -1);
        int n_eles = get_collection<int>(event, eleCountSrc, -1);
        branch_vars.vars_int["n_muons"] = n_muons;
        branch_vars.vars_int["n_eles"] = n_eles;*/
        
        
        branch_vars.vars_float["mu_pt"] = get_collection_n<float>(event, muonPtSrc, 0);
        branch_vars.vars_float["mu_iso"] = get_collection_n<float>(event, muonRelIsoSrc, 0);
        
        //branch_vars.vars_int["mu_charge"] = (int)get_collection_n<float>(event, muonChargeSrc, 0);
        std::string decay_tree = get_collection<std::string>(event, muonDecayTreeSrc, default_str);
        if(decay_tree.size()>0) {
            branch_vars.vars_int["mu_mother_id"] = get_parent(decay_tree, 13);            
        }
        
        post_process();
        return true;
    }
};

class ElectronCuts : public CutsBase {
public:
  bool requireOneElectron;
  float isoCut;

  edm::InputTag eleCountSrc;
  edm::InputTag muonCountSrc;
  edm::InputTag electronRelIsoSrc;
  edm::InputTag electronMvaSrc;
  edm::InputTag electronPtSrc;
  edm::InputTag electronMotherPdgIdSrc;
  edm::InputTag electronChargeSrc;
  edm::InputTag electronDecayTreeSrc;

  virtual void initialize_branches() {
    //branch_vars.vars_float["el_reliso"] = BranchVars::def_val;
    branch_vars.vars_int["el_mother_id"] = BranchVars::def_val_int;
    //branch_vars.vars_int["el_charge"] = BranchVars::def_val_int;
  }
  
  ElectronCuts(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
    CutsBase(_branch_vars)
  {
    initialize_branches();
    //electronRelIsoSrc = pars.getParameter<edm::InputTag>("electronRelIsoSrc");
    electronMotherPdgIdSrc = pars.getParameter<edm::InputTag>("electronMotherPdgIdSrc");
    //electronChargeSrc = pars.getParameter<edm::InputTag>("electronChargeSrc");
    electronDecayTreeSrc = pars.getParameter<edm::InputTag>("electronDecayTreeSrc");
  }
  
  bool process(const edm::EventBase& event){
    pre_process();

    //int n_muons = get_collection<int>(event, muonCountSrc, -1);
    //int n_eles = get_collection<int>(event, eleCountSrc, -1);

    //branch_vars.vars_float["el_reliso"] = get_collection_n<float>(event, electronRelIsoSrc, 0);
    std::string decay_tree = get_collection<std::string>(event, electronDecayTreeSrc, default_str);
    if(decay_tree.size()>0) {
        branch_vars.vars_int["el_mother_id"] = get_parent(decay_tree, 11);
    }
    
    post_process();
    return true;
  }
};

class Weights : public CutsBase {
public:
    edm::InputTag bWeightNominalSrc;
    edm::InputTag puWeightSrc;
    
    edm::InputTag muonIDWeightSrc;
    edm::InputTag muonIsoWeightSrc;
    edm::InputTag muonTriggerWeightSrc;

    edm::InputTag electronIDWeightSrc;
    edm::InputTag electronTriggerWeightSrc;
    
    bool doWeights;
    void initialize_branches() {
        branch_vars.vars_float["b_weight_nominal"] = 1.0;
        branch_vars.vars_float["pu_weight"] = 1.0;
        branch_vars.vars_float["muon_IDWeight"] = 1.0;
        branch_vars.vars_float["muon_IsoWeight"] = 1.0;
        branch_vars.vars_float["muon_TriggerWeight"] = 1.0;
        branch_vars.vars_float["electron_IDWeight"] = 1.0;
        branch_vars.vars_float["electron_triggerWeight"] = 1.0;
    }
    
    Weights(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
    CutsBase(_branch_vars)
    {
        initialize_branches();
        doWeights = pars.getParameter<bool>("doWeights");
        
        bWeightNominalSrc = pars.getParameter<edm::InputTag>("bWeightNominalSrc");
        puWeightSrc = pars.getParameter<edm::InputTag>("puWeightSrc");
        
        muonIDWeightSrc = pars.getParameter<edm::InputTag>("muonIDWeightSrc");
        muonIsoWeightSrc = pars.getParameter<edm::InputTag>("muonIsoWeightSrc");
        muonTriggerWeightSrc = pars.getParameter<edm::InputTag>("muonTriggerWeightSrc");
        
        electronIDWeightSrc = pars.getParameter<edm::InputTag>("electronIDWeightSrc");
        electronTriggerWeightSrc = pars.getParameter<edm::InputTag>("electronTriggerWeightSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars.vars_float["b_weight_nominal"] = get_collection<double>(event, bWeightNominalSrc, 0.0);
        branch_vars.vars_float["pu_weight"] = get_collection<double>(event, puWeightSrc, 0.0);
        
        branch_vars.vars_float["muon_IDWeight"] = get_collection<double>(event, muonIDWeightSrc, 0.0);
        branch_vars.vars_float["muon_IsoWeight"] = get_collection<double>(event, muonIsoWeightSrc, 0.0);
        branch_vars.vars_float["muon_TriggerWeight"] = get_collection<double>(event, muonTriggerWeightSrc, 0.0);
        
        branch_vars.vars_float["electron_IDWeight"] = get_collection<double>(event, electronIDWeightSrc, 0.0);
        branch_vars.vars_float["electron_triggerWeight"] = get_collection<double>(event, electronTriggerWeightSrc, 0.0);

        //Remove NaN weights
        auto not_nan = [&branch_vars] (const std::string& key) {
            if (branch_vars.vars_float[key] != branch_vars.vars_float[key]) {
                branch_vars.vars_float[key] = 0.0;
            }
        };

        not_nan("b_weight_nominal");
        not_nan("pu_weight");

        not_nan("muon_IDWeight");
        not_nan("muon_IsoWeight");
        not_nan("muon_TriggerWeight");
	    
        not_nan("electron_IDWeight");
	    not_nan("electron_triggerWeight");

        post_process();
        
        return true;
    }
};
/*
class MiscVars : public CutsBase {
public:
    edm::InputTag cosThetaSrc;
    edm::InputTag nVerticesSrc;
    edm::InputTag scaleFactorsSrc;

    void initialize_branches() {
        branch_vars.vars_float["cos_theta"] = BranchVars::def_val;
        branch_vars.vars_int["n_vertices"] = BranchVars::def_val;
	//branch_vars_vec["scale_factors"] = std::vector<float>();
        //branch_vars_vec["scale_factors"].clear();
    }

    
    MiscVars(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
    CutsBase(_branch_vars)
    {
        initialize_branches();
        cosThetaSrc = pars.getParameter<edm::InputTag>("cosThetaSrc");
        nVerticesSrc = pars.getParameter<edm::InputTag>("nVerticesSrc");
        //scaleFactorsSrc = pars.getParameter<edm::InputTag>("scaleFactorsSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars.vars_float["cos_theta"] = get_collection<double>(event, cosThetaSrc, BranchVars::def_val);
        branch_vars.vars_int["n_vertices"] = get_collection<int>(event, nVerticesSrc, BranchVars::def_val_int);
        post_process();
        return true;
    }
};
*/
class GenParticles : public CutsBase {
public:
    edm::InputTag trueBJetCount;
    edm::InputTag trueCJetCount;
    edm::InputTag trueLJetCount;
    edm::InputTag trueBJetTaggedCount;
    edm::InputTag trueCJetTaggedCount;
    edm::InputTag trueLJetTaggedCount;
    edm::InputTag trueTopMassSrc;    
    edm::InputTag trueCosTheta;
    edm::InputTag trueLeptonPdgIdSrc;

    bool doGenParticles;
    bool requireGenMuon;
    
    void initialize_branches() {
        /*branch_vars["true_b_count"] = def_val;
        branch_vars["true_c_count"] = def_val;
        branch_vars["true_l_count"] = def_val;
        
        branch_vars["true_b_tagged_count"] = def_val;
        branch_vars["true_c_tagged_count"] = def_val;
        branch_vars["true_l_tagged_count"] = def_val;
    */
        //branch_vars.vars_float["true_top_mass"] = BranchVars::def_val;
        branch_vars.vars_float["true_cos_theta"] = BranchVars::def_val;
        branch_vars.vars_int["true_lepton_pdgId"] = BranchVars::def_val_int;
    }
    
    GenParticles(const edm::ParameterSet& pars, BranchVars& _branch_vars) :
    CutsBase(_branch_vars)    
    {
        initialize_branches();
        
        doGenParticles = pars.getParameter<bool>("doGenParticles");

        /*trueBJetCount = pars.getParameter<edm::InputTag>("trueBJetCountSrc");
        trueCJetCount = pars.getParameter<edm::InputTag>("trueCJetCountSrc");
        trueLJetCount = pars.getParameter<edm::InputTag>("trueLJetCountSrc");
        trueBJetTaggedCount = pars.getParameter<edm::InputTag>("trueBJetTaggedCountSrc");
        trueCJetTaggedCount = pars.getParameter<edm::InputTag>("trueCJetTaggedCountSrc");
        trueLJetTaggedCount = pars.getParameter<edm::InputTag>("trueLJetTaggedCountSrc");*/
        //trueTopMassSrc = pars.getParameter<edm::InputTag>("trueTopMassSrc");
        trueCosTheta = pars.getParameter<edm::InputTag>("trueCosThetaSrc");
        trueLeptonPdgIdSrc = pars.getParameter<edm::InputTag>("trueLeptonPdgIdSrc");
		requireGenMuon = pars.getParameter<bool>("requireGenMuon");		  
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        /*branch_vars["true_b_count"] = get_collection<int>(event, trueBJetCount, def_val);
        branch_vars["true_c_count"] = get_collection<int>(event, trueCJetCount, def_val);
        branch_vars["true_l_count"] = get_collection<int>(event, trueLJetCount, def_val);
        
        branch_vars["true_b_tagged_count"] = get_collection<int>(event, trueBJetTaggedCount, def_val);
        branch_vars["true_c_tagged_count"] = get_collection<int>(event, trueCJetTaggedCount, def_val);
        branch_vars["true_l_tagged_count"] = get_collection<int>(event, trueLJetTaggedCount, def_val);*/

        //branch_vars.vars_float["true_top_mass"] = get_collection_n<float>(event, trueTopMassSrc, BranchVars::def_val);
        branch_vars.vars_float["true_cos_theta"] = (float)get_collection<double>(event, trueCosTheta, BranchVars::def_val);
        branch_vars.vars_int["true_lepton_pdgId"] = get_collection<int>(event, trueLeptonPdgIdSrc, 0);
		  	
		if(requireGenMuon && abs(branch_vars.vars_int["true_lepton_pdgId"])!=13) return false;

        post_process();
        return true;
    }
};

//class LumiBlockCounters {
//    std::vector<edm::InputTag> counter_srcs;
//
//    initialize
//    LumiBlockCounters(const edm::ParameterSet& pars) {
//        counter_srcs(pars.getParameter<std::vector<edm::InputTag>>("trackedCounters"));
//    }
//};


int main(int argc, char* argv[])
{    
    // load framework libraries
    gSystem->Load( "libFWCoreFWLite" );
    AutoLibraryLoader::enable();
    
    if ( argc < 2 ) {
        std::cout << "Usage : " << argv[0] << " [parameters.py]" << std::endl;
        return 0;
    }
    
    PythonProcessDesc builder(argv[1], argc, argv);
    const edm::ParameterSet& in  = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("fwliteInput" );
    const edm::ParameterSet& out = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("fwliteOutput");
    
    std::string outputFile_( out.getParameter<std::string>("fileName" ) );
    std::vector<std::string> inputFiles_( in.getParameter<std::vector<std::string> >("fileNames") );
    
    //const edm::ParameterSet& mu_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("muonCuts");    
    //const edm::ParameterSet& ele_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("eleCuts");

    const edm::ParameterSet& weight_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("weights");
    //const edm::ParameterSet& miscvars_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("finalVars");
    const edm::ParameterSet& gen_particle_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("genParticles");
    
    const edm::ParameterSet& lumiblock_counter_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("lumiBlockCounters");
    edm::InputTag totalPATProcessedCountSrc = lumiblock_counter_pars.getParameter<edm::InputTag>("totalPATProcessedCountSrc");
    
    BranchVars branch_vars; 
    std::map<std::string, unsigned int> event_id_branches;
    std::map<std::string, unsigned int> count_map;

    std::vector<std::string> count_map_order({
        "total_processed", 
	    //"pass_muon_cuts", "pass_electron_cuts", 
        "pass_gen_cuts"
	  });
   
    for(auto& e : count_map_order) {
        count_map[e] = 0; 
    }

    //MuonCuts muon_cuts(mu_cuts_pars, branch_vars);
    //ElectronCuts electron_cuts(ele_cuts_pars, branch_vars);
    Weights weights(weight_pars, branch_vars);
    //MiscVars misc_vars(miscvars_pars, branch_vars);
    GenParticles gen_particles(gen_particle_pars, branch_vars);
    

    fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());
    
    // now get each parameter
    int maxEvents_( in.getParameter<int>("maxEvents") );
    unsigned int outputEvery_( in.getParameter<unsigned int>("outputEvery") );
    
    TFileDirectory dir = fs.mkdir("trees");
    TTree* out_tree = dir.make<TTree>("Events", "Events");
    TH1I* count_hist = dir.make<TH1I>("count_hist", "Event counts", count_map.size(), 0, count_map.size() - 1);
    
    TFile::SetOpenTimeout(60000);
    if(!TFile::SetCacheFileDir("/scratch/andres")) {
        std::cerr << "Cache directory was not writable" << std::endl;
    }
    
    event_id_branches["event_id"] = -1;
    event_id_branches["run_id"] = -1;
    event_id_branches["lumi_id"] = -1;
   
    
    //Create all the requested branches in the TTree
    LogInfo << "Creating branches: ";
    for (auto & elem : branch_vars.vars_float) {
        const std::string& br_name = elem.first;
        std::cout << br_name << ", ";
        float* p_branch = &(elem.second);
        out_tree->Branch(br_name.c_str(), p_branch);
    }
    for (auto & elem : branch_vars.vars_int) {
        const std::string& br_name = elem.first;
        std::cout << br_name << ", ";
        int* p_branch = &(elem.second);
        out_tree->Branch(br_name.c_str(), p_branch);
    }
    for (auto & elem : branch_vars.vars_vfloat) {
        std::cout << elem.first << ", ";
        out_tree->Branch(elem.first.c_str(), &(elem.second));
    }
    for (auto & elem : event_id_branches) {
        const std::string& br_name = elem.first;
        std::cout << br_name << ", ";
        unsigned int* p_branch = &(elem.second);
        out_tree->Branch(br_name.c_str(), p_branch);
    }
    std::cout << std::endl;
    
    // loop the events
    int ievt=0;
    long bytes_read = 0;
    TStopwatch* stopwatch = new TStopwatch();
    stopwatch->Start();
    for(unsigned int iFile=0; iFile<inputFiles_.size(); ++iFile) {
        // open input file (can be located on castor)
        LogInfo << "Opening file " << inputFiles_[iFile] << std::endl;
        TFile* in_file = TFile::Open(inputFiles_[iFile].c_str());
        if( in_file ) {
            LogInfo << "File opened successfully" << std::endl; 
            double file_time = stopwatch->RealTime();
            stopwatch->Continue();
            
            fwlite::Event ev(in_file);
            for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt) {
                edm::EventBase const & event = ev;
                
                //muon_cuts.initialize_branches();
        		//electron_cuts.initialize_branches();
                // break loop if maximal number of events is reached
                if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
                
                if(outputEvery_!=0 ? (ievt>0 && ievt%outputEvery_==0) : false)
                    LogInfo << "processing event: " << ievt << std::endl;
                
                /*bool passes_muon_cuts = muon_cuts.process(event);
                if(!passes_muon_cuts) continue;
                
                bool passes_electron_cuts = electron_cuts.process(event);
                if(!passes_electron_cuts) continue;
                */
                //misc_vars.process(event);
                //if(weights.doWeights) weights.process(event);
                
                bool passes_gen_cuts = true;
                if (gen_particles.doGenParticles) {
                     passes_gen_cuts = gen_particles.process(event);
                }
                if(!passes_gen_cuts) continue;

                event_id_branches["event_id"] = (unsigned int)event.id().event();
                event_id_branches["run_id"] = (unsigned int)event.id().run();
                event_id_branches["lumi_id"] = (unsigned int)event.id().luminosityBlock();
                
                out_tree->Fill();
            }
            
            fwlite::LuminosityBlock ls(in_file);
            
            //long count_events = 0;
            for(ls.toBegin(); !ls.atEnd(); ++ls) {
                edm::Handle<edm::MergeableCounter> counter;
                ls.getByLabel(totalPATProcessedCountSrc, counter);
                count_map["total_processed"] += counter->value;
            }
            in_file->Close();
            file_time = stopwatch->RealTime() - file_time;
            stopwatch->Continue();
            bytes_read += in_file->GetBytesRead();
            LogInfo << "Closing file " << in_file->GetPath() << " with " << in_file->GetBytesRead()/(1024*1024) << " Mb read, "
                    << in_file->GetBytesRead()/(1024*1024) / file_time << " Mb/s" << std::endl;
        }
    }
    
    //count_map["pass_muon_cuts"] += muon_cuts.n_pass;
    //count_map["pass_electron_cuts"] += electron_cuts.n_pass;
    count_map["pass_gen_cuts"] += gen_particles.n_pass;
    
    int i = 1;
    for (auto& elem : count_map_order) {
        count_hist->AddBinContent(i, count_map[elem]);
        count_hist->GetXaxis()->SetBinLabel(i, elem.c_str());
        i++;
    }
    
    std::cout << "total processed step1 " << count_map["total_processed"] << std::endl;
    std::cout << "total processed step3 " << ievt << std::endl;
    //std::cout << "muon cuts " << muon_cuts.toString() << std::endl;
    //std::cout << "electron cuts " << electron_cuts.toString() << std::endl;
    std::cout << "gen cuts " << gen_particles.toString() << std::endl;
    stopwatch->Stop();
    
    double time = stopwatch->RealTime();
    int speed = (int)((float)ievt / time);
    int mb_total = bytes_read/(1024*1024);
    LogInfo << "processing speed = " << speed << " events/sec" << std::endl;
    LogInfo << "read " << mb_total << " Mb in total, average speed " << (double)mb_total / time << " Mb/s" << std::endl;  
    //    for (auto& elem : cut_count_map) {
    //        std::cout << elem.first << " " << elem.second << std::endl;
    //    }
    
    return 0;
}
