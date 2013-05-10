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
#include "hlt_cuts.h"

#include <stdio.h>
#include <time.h>

using namespace std;

namespace LHAPDF
{
	void initPDFSet(int nset, const std::string &filename, int member = 0);
	int numberPDF(int nset);
	void usePDFMember(int nset, int member);
	double xfx(int nset, double x, double Q, int fl);
	double getXmin(int nset, int member);
	double getXmax(int nset, int member);
	double getQ2min(int nset, int member);
	double getQ2max(int nset, int member);
	void extrapolate(bool extrapolate = true);
	int	numberPDF();
}

//Shorthand for getting a value of type T from the event
template <typename T>
T get_collection(const edm::EventBase& evt, edm::InputTag src, const T& retval) {
    edm::Handle<T> coll;
    evt.getByLabel(src, coll);
    if(!coll.isValid()) {
        //std::cerr << "Collection " << src.label() << " is not valid!" << std::endl;
        return retval;
    }
    return *coll;
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

//The default value for a TTree entry
static const float def_val = (const float)(TMath::QuietNaN());

class MuonCuts : public CutsBaseF {
public:
    bool cutOnIso;
    bool reverseIsoCut;
    bool requireOneMuon;
    bool doControlVars;
    
    float isoCut;
    edm::InputTag muonPtSrc;
    edm::InputTag muonRelIsoSrc;
    edm::InputTag muonCountSrc;
    edm::InputTag eleCountSrc;
    
    edm::InputTag muonDbSrc;
    edm::InputTag muonDzSrc;
    edm::InputTag muonNormChi2Src;
    edm::InputTag muonChargeSrc;

    edm::InputTag muonGTrackHitsSrc;
    edm::InputTag muonITrackHitsSrc;
    edm::InputTag muonLayersSrc;
    edm::InputTag muonStationsSrc;

    virtual void initialize_branches() {
        branch_vars["mu_pt"] = def_val;
        branch_vars["mu_iso"] = def_val;
        
        branch_vars["n_muons"] = def_val;
        branch_vars["n_eles"] = def_val;
        
        if(doControlVars) {
            branch_vars["mu_db"] = def_val;
            branch_vars["mu_dz"] = def_val;
            branch_vars["mu_chi2"] = def_val;
            branch_vars["mu_charge"] = def_val;
            branch_vars["mu_gtrack"] = def_val;
            branch_vars["mu_itrack"] = def_val;
            branch_vars["mu_layers"] = def_val;
            branch_vars["mu_stations"] = def_val;

        }
    }
    
    MuonCuts(const edm::ParameterSet& pars, std::map< std::string, float> & _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        requireOneMuon = pars.getParameter<bool>("requireOneMuon");
        
        cutOnIso = pars.getParameter<bool>("cutOnIso");
        doControlVars = pars.getParameter<bool>("doControlVars");
        reverseIsoCut = pars.getParameter<bool>("reverseIsoCut");
        isoCut = (float)pars.getParameter<double>("isoCut");
        
        muonPtSrc = pars.getParameter<edm::InputTag>("muonPtSrc");
        muonRelIsoSrc = pars.getParameter<edm::InputTag>("muonRelIsoSrc");
        
        if(doControlVars) {
            muonDbSrc = pars.getParameter<edm::InputTag>("muonDbSrc");
            muonDzSrc = pars.getParameter<edm::InputTag>("muonDzSrc");
            muonNormChi2Src = pars.getParameter<edm::InputTag>("muonNormChi2Src");
            muonChargeSrc = pars.getParameter<edm::InputTag>("muonChargeSrc");

            muonGTrackHitsSrc = pars.getParameter<edm::InputTag>("muonGTrackHitsSrc");
            muonITrackHitsSrc = pars.getParameter<edm::InputTag>("muonITrackHitsSrc");
            muonLayersSrc = pars.getParameter<edm::InputTag>("muonLayersSrc");
            muonStationsSrc = pars.getParameter<edm::InputTag>("muonStationsSrc");
        }
        
        muonCountSrc = pars.getParameter<edm::InputTag>("muonCountSrc"); 
        eleCountSrc = pars.getParameter<edm::InputTag>("eleCountSrc"); 
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        int n_muons = get_collection<int>(event, muonCountSrc, -1);
        int n_eles = get_collection<int>(event, eleCountSrc, -1);
        branch_vars["n_muons"] = (float)n_muons;
        branch_vars["n_eles"] = (float)n_eles;
        if(requireOneMuon && (n_muons!=1 || n_eles !=0)) return false;
        
        branch_vars["mu_pt"] = get_collection_n<float>(event, muonPtSrc, 0);
        branch_vars["mu_iso"] = get_collection_n<float>(event, muonRelIsoSrc, 0);
        
        if(doControlVars) {
            branch_vars["mu_db"] = get_collection_n<float>(event, muonDbSrc, 0);
            branch_vars["mu_dz"] = get_collection_n<float>(event, muonDzSrc, 0);
            branch_vars["mu_chi2"] = get_collection_n<float>(event, muonNormChi2Src, 0);
            branch_vars["mu_charge"] = get_collection_n<float>(event, muonChargeSrc, 0);
            branch_vars["mu_gtrack"] = get_collection_n<float>(event, muonGTrackHitsSrc, 0);
            branch_vars["mu_itrack"] = get_collection_n<float>(event, muonITrackHitsSrc, 0);
            branch_vars["mu_layers"] = get_collection_n<float>(event, muonLayersSrc, 0);
            branch_vars["mu_stations"] = get_collection_n<float>(event, muonStationsSrc, 0);
        }
        
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

class VetoLeptonCuts : public CutsBaseF {
public:
    bool doVetoLeptonCut;
    edm::InputTag vetoMuCountSrc;
    edm::InputTag vetoEleCountSrc;
   
    void initialize_branches() {
        branch_vars["n_veto_mu"] = -1.0;
        branch_vars["n_veto_ele"] = -1.0;
    }

    VetoLeptonCuts(const edm::ParameterSet& pars, std::map< std::string, float> & _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        doVetoLeptonCut = pars.getParameter<bool>("doVetoLeptonCut");
        vetoMuCountSrc = pars.getParameter<edm::InputTag>("vetoMuCountSrc");
        vetoEleCountSrc = pars.getParameter<edm::InputTag>("vetoEleCountSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        int n_veto_mu = get_collection<int>(event, vetoMuCountSrc, -1);
        int n_veto_ele = get_collection<int>(event, vetoEleCountSrc, -1);
        branch_vars["n_veto_mu"] = (float)n_veto_mu;
        branch_vars["n_veto_ele"] = (float)n_veto_ele;
        if(doVetoLeptonCut) {
            if (n_veto_mu != 0 || n_veto_ele != 0) return false;
        }

        post_process();
        return true;
    }
};

class JetCuts : public CutsBaseF {
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
    float etaMin;
    
    edm::InputTag goodJetsCountSrc;
    edm::InputTag bTagJetsCountSrc;
    
    edm::InputTag goodJetsPtSrc;
    edm::InputTag goodJetsEtaSrc;
    
    edm::InputTag lightJetEtaSrc;
    edm::InputTag lightJetBdiscrSrc;
    edm::InputTag lightJetPtSrc;
    edm::InputTag lightJetRmsSrc;
    edm::InputTag lightJetDeltaRSrc;    

    edm::InputTag bJetEtaSrc;
    edm::InputTag bJetBdiscrSrc;
    edm::InputTag bJetPtSrc;
    edm::InputTag bJetDeltaRSrc;
    
    virtual void initialize_branches() {
        branch_vars["pt_lj"] = def_val;
        branch_vars["eta_lj"] = def_val;
        branch_vars["bdiscr_lj"] = def_val;
        branch_vars["rms_lj"] = def_val;
        branch_vars["deltaR_lj"] = def_val;
        
        branch_vars["pt_bj"] = def_val;
        branch_vars["eta_bj"] = def_val;
        branch_vars["bdiscr_bj"] = def_val;
        
        branch_vars["n_jets"] = def_val;
        branch_vars["n_tags"] = def_val;
    }
    
    JetCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        cutOnNJets =  pars.getParameter<bool>("cutOnNJets");
        applyRmsLj =  pars.getParameter<bool>("applyRmsLj");
        applyEtaLj =  pars.getParameter<bool>("applyEtaLj");
        
        rmsMax = pars.getParameter<double>("rmsMax");
        etaMin = pars.getParameter<double>("etaMin");

        nJetsCutMax = pars.getParameter<int>("nJetsMax");
        nJetsCutMin = pars.getParameter<int>("nJetsMin");
        
        goodJetsCountSrc = pars.getParameter<edm::InputTag>("goodJetsCountSrc");
        
        goodJetsPtSrc = pars.getParameter<edm::InputTag>("goodJetsPtSrc");
        goodJetsEtaSrc = pars.getParameter<edm::InputTag>("goodJetsEtaSrc");
        
        lightJetEtaSrc = pars.getParameter<edm::InputTag>("lightJetEtaSrc");
        lightJetBdiscrSrc = pars.getParameter<edm::InputTag>("lightJetBdiscrSrc");
        lightJetPtSrc = pars.getParameter<edm::InputTag>("lightJetPtSrc");
        lightJetRmsSrc = pars.getParameter<edm::InputTag>("lightJetRmsSrc");
        lightJetDeltaRSrc = pars.getParameter<edm::InputTag>("lightJetDeltaRSrc");
        
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        branch_vars["pt_lj"] = get_collection_n<float>(event, lightJetPtSrc, 0);
        branch_vars["eta_lj"] = get_collection_n<float>(event, lightJetEtaSrc, 0);
        branch_vars["bdiscr_lj"] = get_collection_n<float>(event, lightJetBdiscrSrc, 0);
        branch_vars["rms_lj"] = get_collection_n<float>(event, lightJetRmsSrc, 0);
        branch_vars["deltaR_lj"] = get_collection_n<float>(event, lightJetDeltaRSrc, 0);
        bool passes_rms_lj = (branch_vars["rms_lj"] < rmsMax);
        bool passes_eta_lj = (abs(branch_vars["eta_lj"]) > etaMin);

        branch_vars["n_jets"] = get_collection<int>(event, goodJetsCountSrc, -1);
        
        if (cutOnNJets && (branch_vars["n_jets"] > nJetsCutMax || branch_vars["n_jets"] < nJetsCutMin)) return false;
        if (applyRmsLj && !passes_rms_lj) return false;
        if (applyEtaLj && !passes_eta_lj) return false;

        post_process();
        return true;
    }
};

class TagCuts : public CutsBaseF {
public:
    bool cutOnNTags;
    
    int nTagsCutMin;
    int nTagsCutMax;
    
    edm::InputTag bJetEtaSrc;
    edm::InputTag bJetBdiscrSrc;
    edm::InputTag bJetPtSrc;
    edm::InputTag bTagJetsCountSrc;
    edm::InputTag bJetDeltaRSrc;
    
    virtual void initialize_branches() {
        branch_vars["pt_bj"] = def_val;
        branch_vars["eta_bj"] = def_val;
        branch_vars["bdiscr_bj"] = def_val;
        branch_vars["n_tags"] = def_val;
        branch_vars["deltaR_bj"] = def_val;
    }
    
    TagCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        cutOnNTags =  pars.getParameter<bool>("cutOnNTags");
        nTagsCutMax = pars.getParameter<int>("nTagsMax");
        nTagsCutMin = pars.getParameter<int>("nTagsMin");
        
        bJetEtaSrc = pars.getParameter<edm::InputTag>("bJetEtaSrc");
        bJetBdiscrSrc = pars.getParameter<edm::InputTag>("bJetBdiscrSrc");
        bJetPtSrc = pars.getParameter<edm::InputTag>("bJetPtSrc");
        bTagJetsCountSrc = pars.getParameter<edm::InputTag>("bTagJetsCountSrc");
        bJetDeltaRSrc = pars.getParameter<edm::InputTag>("bJetDeltaRSrc");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["pt_bj"] = get_collection_n<float>(event, bJetPtSrc, 0);
        branch_vars["eta_bj"] = get_collection_n<float>(event, bJetEtaSrc, 0);
        branch_vars["bdiscr_bj"] = get_collection_n<float>(event, bJetBdiscrSrc, 0);
        branch_vars["n_tags"] = get_collection<int>(event, bTagJetsCountSrc, -1);
        branch_vars["deltaR_bj"] = get_collection_n<float>(event, bJetDeltaRSrc, 0);

        if (cutOnNTags && (branch_vars["n_tags"] > nTagsCutMax || branch_vars["n_tags"] < nTagsCutMin)) return false;
        
        post_process();
        return true;
    }
};

class TopCuts : public CutsBaseF {
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
    CutsBaseF(_branch_vars)
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

class Weights : public CutsBaseF {
public:
    edm::InputTag bWeightNominalSrc;
    edm::InputTag puWeightSrc;
    edm::InputTag muonIDWeightSrc;
    edm::InputTag muonIsoWeightSrc;
    
    bool doWeights;
    void initialize_branches() {
        branch_vars["b_weight_nominal"] = 1.0;
        branch_vars["pu_weight"] = 1.0;
        branch_vars["muon_IDWeight"] = 1.0;
        branch_vars["muon_IsoWeight"] = 1.0;
    }
    
    Weights(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        doWeights = pars.getParameter<bool>("doWeights");
        
        bWeightNominalSrc = pars.getParameter<edm::InputTag>("bWeightNominalSrc");
        puWeightSrc = pars.getParameter<edm::InputTag>("puWeightSrc");
        muonIDWeightSrc = pars.getParameter<edm::InputTag>("muonIDWeightSrc");
        muonIsoWeightSrc = pars.getParameter<edm::InputTag>("muonIsoWeightSrc");
        
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["b_weight_nominal"] = get_collection<double>(event, bWeightNominalSrc, def_val);
        branch_vars["pu_weight"] = get_collection<double>(event, puWeightSrc, def_val);
        branch_vars["muon_IDWeight"] = get_collection<double>(event, muonIDWeightSrc, def_val);
        branch_vars["muon_IsoWeight"] = get_collection<double>(event, muonIsoWeightSrc, def_val);
       
        //Remove NaN weights
        auto not_nan = [&branch_vars] (const std::string& key) {
            if (branch_vars[key] != branch_vars[key]) {
                branch_vars[key] = 0.0;
            }
        };

        not_nan("b_weight_nominal");
        not_nan("pu_weight");
        not_nan("muon_IDWeight");
        not_nan("muon_IsoWeight");
        
        post_process();
        return true;
    }
};

class MTMuCuts : public CutsBaseF {
public:
    edm::InputTag mtMuSrc;
    edm::InputTag metSrc;
    float minVal;
    bool doMTCut;
    
    void initialize_branches() {
        branch_vars["mt_mu"] = def_val;
        branch_vars["met"] = def_val;
    }
    
    MTMuCuts(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        mtMuSrc = pars.getParameter<edm::InputTag>("mtMuSrc");
        metSrc = pars.getParameter<edm::InputTag>("metSrc");
        minVal = (float)pars.getParameter<double>("minVal");
        doMTCut = pars.getParameter<bool>("doMTCut");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["mt_mu"] = get_collection<double>(event, mtMuSrc, def_val);
        branch_vars["met"] = get_collection_n<float>(event, metSrc, 0);
        if (doMTCut && branch_vars["mt_mu"] < minVal) return false;
        
        post_process();
        return true;
    }
};

class MiscVars : public CutsBaseF {
public:
    edm::InputTag cosThetaSrc;
    edm::InputTag nVerticesSrc;
    edm::InputTag scaleFactorsSrc;
    
    std::map<std::string, std::vector<float>>& branch_vars_vec;
    
    // for PDF uncertanty
    bool addPDFInfo;
    edm::InputTag scalePDFSrc;
    edm::InputTag x1Src;
    edm::InputTag x2Src;
    edm::InputTag id1Src;
    edm::InputTag id2Src;

    float	scalePDF;
	float	x1,x2;
	int		id1,id2;
	
	std::vector<std::string>	PDFSets;
	std::vector<std::string>	PDFnames;
	
    void initialize_branches() {
        branch_vars["cos_theta"] = def_val;
        branch_vars["n_vertices"] = def_val;
        //branch_vars_vec["scale_factors"] = std::vector<float>();
        //branch_vars_vec["scale_factors"].clear();
    }

    void initialize_branches_PDF(bool addPDFs) {
        if(!addPDFs) return;		
    	branch_vars["scalePDF"] = def_val;
		branch_vars["x1"] = def_val;
		branch_vars["x2"] = def_val;
		branch_vars["id1"] = def_val;
		branch_vars["id2"] = def_val;
    }
    
    
    MiscVars(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars, std::map<std::string, std::vector<float>>& _branch_vars_vec) :
    CutsBaseF(_branch_vars),
    branch_vars_vec(_branch_vars_vec)
    {
        addPDFInfo = pars.getParameter<bool>("addPDFInfo");
        if(addPDFInfo){
            PDFSets = pars.getParameter<std::vector<std::string>>("PDFSets");
            std::map<string,int> map_name;
            //cout << "size " << PDFSets.size() <<endl;
            for( unsigned int i = 0; i < PDFSets.size(); i++ ){
                if( i > 2 ) break;	// lhapdf cannot manage with more PDFs 

            	// make names of PDF sets to be saved
            	string name = PDFSets[i];
            	size_t pos = name.find_first_not_of("ZXCVBNMASDFGHJKLQWERTYUIOPabcdefghijklmnopqrstuvwxyz1234567890");
            	if (pos!=std::string::npos) name = name.substr(0,pos);
            	if( map_name.count(name) == 0 ){
            		map_name[name]=0;
            		PDFnames.push_back(name);
            	}
            	else {
            		map_name[name]++;
            		ostringstream ostr;
            		ostr << name << "xxx" << map_name[name];
            		PDFnames.push_back(ostr.str());
            	}
            
                // initialise the PDF set
            	//cout<<"PDFnames[i]="<<PDFnames[i]<<"\tPDFSets[i]="<<PDFSets[i]<<endl;
    		    LHAPDF::initPDFSet(i+1, PDFSets[i]);
                branch_vars[string("w0"+PDFnames[i])] = def_val;
                branch_vars[string("n"+PDFnames[i])] = def_val;
                branch_vars_vec[string("weights"+PDFnames[i])] = std::vector<float>();
                branch_vars_vec[string("weights"+PDFnames[i])].clear();
    	    }
        }
        initialize_branches();
        cosThetaSrc = pars.getParameter<edm::InputTag>("cosThetaSrc");
        nVerticesSrc = pars.getParameter<edm::InputTag>("nVerticesSrc");
        //scaleFactorsSrc = pars.getParameter<edm::InputTag>("scaleFactorsSrc");

        if(addPDFInfo){
    		scalePDFSrc = pars.getParameter<edm::InputTag>("scalePDFSrc");
    		x1Src = pars.getParameter<edm::InputTag>("x1Src");
    		x2Src = pars.getParameter<edm::InputTag>("x2Src");
    		id1Src = pars.getParameter<edm::InputTag>("id1Src");
    		id2Src = pars.getParameter<edm::InputTag>("id2Src");
        }
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["cos_theta"] = get_collection<double>(event, cosThetaSrc, def_val);
        branch_vars["n_vertices"] = get_collection<int>(event, nVerticesSrc, def_val);

        //edm::Handle<std::vector<float>> scale_factors;
        //event.getByLabel(scaleFactorsSrc, scale_factors);
        //if(scale_factors.isValid()) {
        //    for (auto sf : *scale_factors) {
        //        branch_vars_vec["scale_factors"].push_back(sf);
        //    }
        //}

        // for PDF uncertanty
        if(addPDFInfo){
            branch_vars["scalePDF"] = get_collection<float>(event, scalePDFSrc, def_val);
    		branch_vars["x1"] = get_collection<float>(event, x1Src, def_val);
    		branch_vars["x2"] = get_collection<float>(event, x2Src, def_val);
    		branch_vars["id1"] = get_collection<int>(event, id1Src, def_val);
    		branch_vars["id2"] = get_collection<int>(event, id2Src, def_val);

        	
            for( unsigned int i = 0; i < PDFSets.size(); i++ ){
        		if( i > 2 ) break;	// lhapdf cannot manage with more PDFs 
        		
        		int InitNr = i+1;
        		
        		// calculate the PDF weights
        		std::auto_ptr < std::vector<double> > weights(new std::vector<double>());
        		LHAPDF::usePDFMember(InitNr, 0);
                double	xpdf1	= LHAPDF::xfx(InitNr, branch_vars["x1"], branch_vars["scalePDF"], branch_vars["id1"]);
        		double	xpdf2	= LHAPDF::xfx(InitNr, branch_vars["x2"], branch_vars["scalePDF"], branch_vars["id2"]);
        		double	w0		= xpdf1 * xpdf2;
        		int		nPDFSet = LHAPDF::numberPDF(InitNr);
        		for (int p = 1; p <= nPDFSet; p++)
        		{
        			LHAPDF::usePDFMember(InitNr, p);
        			double xpdf1_new	= LHAPDF::xfx(InitNr, branch_vars["x1"], branch_vars["scalePDF"], branch_vars["id1"]);
        			double xpdf2_new	= LHAPDF::xfx(InitNr, branch_vars["x2"], branch_vars["scalePDF"], branch_vars["id2"]);
        			double pweight		= xpdf1_new * xpdf2_new / w0;
        			weights->push_back(pweight);
        		}
        		
        		// save weights
                for (auto sf : (*weights)) {
                    branch_vars_vec[std::string("weights"+PDFnames[i])].push_back(float(sf));
                }
                branch_vars[std::string("n"+PDFnames[i])] = nPDFSet;
                branch_vars[std::string("w0"+PDFnames[i])] = w0;
        	}
        }
        post_process();
        return true;
    }
};

class GenParticles : public CutsBaseF {
public:
    edm::InputTag trueBJetCount;
    edm::InputTag trueCJetCount;
    edm::InputTag trueLJetCount;
    edm::InputTag trueBJetTaggedCount;
    edm::InputTag trueCJetTaggedCount;
    edm::InputTag trueLJetTaggedCount;
    edm::InputTag trueCosTheta;
    edm::InputTag trueLeptonPdgIdSrc;

    bool doGenParticles;
    bool requireGenMuon;
    
    void initialize_branches() {
        branch_vars["true_b_count"] = def_val;
        branch_vars["true_c_count"] = def_val;
        branch_vars["true_l_count"] = def_val;
        
        branch_vars["true_b_tagged_count"] = def_val;
        branch_vars["true_c_tagged_count"] = def_val;
        branch_vars["true_l_tagged_count"] = def_val;

        branch_vars["true_cos_theta"] = def_val;
        branch_vars["true_lepton_pdgId"] = def_val;
    }
    
    GenParticles(const edm::ParameterSet& pars, std::map<std::string, float>& _branch_vars) :
    CutsBaseF(_branch_vars)
    {
        initialize_branches();
        
        doGenParticles = pars.getParameter<bool>("doGenParticles");

        trueBJetCount = pars.getParameter<edm::InputTag>("trueBJetCountSrc");
        trueCJetCount = pars.getParameter<edm::InputTag>("trueCJetCountSrc");
        trueLJetCount = pars.getParameter<edm::InputTag>("trueLJetCountSrc");
        trueBJetTaggedCount = pars.getParameter<edm::InputTag>("trueBJetTaggedCountSrc");
        trueCJetTaggedCount = pars.getParameter<edm::InputTag>("trueCJetTaggedCountSrc");
        trueLJetTaggedCount = pars.getParameter<edm::InputTag>("trueLJetTaggedCountSrc");
        
        trueCosTheta = pars.getParameter<edm::InputTag>("trueCosThetaSrc");
        trueLeptonPdgIdSrc = pars.getParameter<edm::InputTag>("trueLeptonPdgIdSrc");
        requireGenMuon = pars.getParameter<bool>("requireGenMuon");
    }
    
    bool process(const edm::EventBase& event) {
        pre_process();
        
        branch_vars["true_b_count"] = get_collection<int>(event, trueBJetCount, def_val);
        branch_vars["true_c_count"] = get_collection<int>(event, trueCJetCount, def_val);
        branch_vars["true_l_count"] = get_collection<int>(event, trueLJetCount, def_val);
        
        branch_vars["true_b_tagged_count"] = get_collection<int>(event, trueBJetTaggedCount, def_val);
        branch_vars["true_c_tagged_count"] = get_collection<int>(event, trueCJetTaggedCount, def_val);
        branch_vars["true_l_tagged_count"] = get_collection<int>(event, trueLJetTaggedCount, def_val);

        branch_vars["true_cos_theta"] = get_collection<double>(event, trueCosTheta, def_val);
        branch_vars["true_lepton_pdgId"] = get_collection<int>(event, trueLeptonPdgIdSrc, 0);
		  	
		if(requireGenMuon && abs(branch_vars["true_lepton_pdgId"])!=13) return false;

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
#define LogInfo std::cout << currentDateTime() << ":"

int main(int argc, char* argv[])
{    
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

    const edm::ParameterSet& btag_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("bTagCuts");

    const edm::ParameterSet& top_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("topCuts");
    const edm::ParameterSet& mt_mu_cuts_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("mtMuCuts");
    const edm::ParameterSet& weight_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("weights");
    const edm::ParameterSet& miscvars_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("finalVars");
    const edm::ParameterSet& gen_particle_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("genParticles");
    const edm::ParameterSet& hlt_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("HLT");
    
    const edm::ParameterSet& lumiblock_counter_pars = builder.processDesc()->getProcessPSet()->getParameter<edm::ParameterSet>("lumiBlockCounters");
    edm::InputTag totalPATProcessedCountSrc = lumiblock_counter_pars.getParameter<edm::InputTag>("totalPATProcessedCountSrc");
    
    std::map<std::string, float> branch_vars;
    std::map<std::string, int> branch_varsI;
    std::map<std::string, std::vector<float> > branch_vars_vec;
    std::map<std::string, unsigned int> event_id_branches;
    std::map<std::string, unsigned int> count_map;

    //Give the order of the map keys that will end up as the count histogram bins
    std::vector<std::string> count_map_order({
        "total_processed", "pass_hlt_cut",
        "pass_lepton_cuts", "pass_lepton_veto_cuts",
        "pass_mt_cuts", "pass_jet_cuts",
        "pass_btag_cuts", "pass_top_cuts",
        "pass_gen_cuts"
    });
   
    for(auto& e : count_map_order) {
        count_map[e] = 0; 
    }

    MuonCuts muon_cuts(mu_cuts_pars, branch_vars);
    VetoLeptonCuts veto_lepton_cuts(mu_cuts_pars, branch_vars);
    JetCuts jet_cuts(jet_cuts_pars, branch_vars);
    TagCuts btag_cuts(btag_cuts_pars, branch_vars);
    TopCuts top_cuts(top_cuts_pars, branch_vars);
    Weights weights(weight_pars, branch_vars);
    MTMuCuts mt_mu_cuts(mt_mu_cuts_pars, branch_vars);
    MiscVars misc_vars(miscvars_pars, branch_vars, branch_vars_vec);
    GenParticles gen_particles(gen_particle_pars, branch_vars);
    HLTCuts hlt_cuts(hlt_pars, branch_varsI);
    
    fwlite::TFileService fs = fwlite::TFileService(outputFile_.c_str());
    
    // now get each parameter
    int maxEvents_( in.getParameter<int>("maxEvents") );
    unsigned int outputEvery_( in.getParameter<unsigned int>("outputEvery") );
    
    TFileDirectory dir = fs.mkdir("trees");
    TTree* out_tree = dir.make<TTree>("Events", "Events");
    TH1I* count_hist = dir.make<TH1I>("count_hist", "Event counts", count_map.size(), 0, count_map.size() - 1);
    
    TFile::SetOpenTimeout(60000);
    if(!TFile::SetCacheFileDir("/scratch/joosep")) {
        std::cerr << "Cache directory was not writable" << std::endl;
    }
    
    event_id_branches["event_id"] = -1;
    event_id_branches["run_id"] = -1;
    event_id_branches["lumi_id"] = -1;
    
    //Create all the requested branches in the TTree
    for (auto & elem : branch_vars) {
        const std::string& br_name = elem.first;
        float* p_branch = &(elem.second);
        out_tree->Branch(br_name.c_str(), p_branch);
    }
    
    //Create all the requested branches in the TTree
    for (auto & elem : branch_varsI) {
        const std::string& br_name = elem.first;
        int* p_branch = &(elem.second);
        out_tree->Branch(br_name.c_str(), p_branch);
    }
    
    for (auto & elem : event_id_branches) {
        out_tree->Branch(elem.first.c_str(), &(elem.second));
    }
    for (auto & elem : branch_vars_vec) {
        out_tree->Branch(elem.first.c_str(), &(elem.second));
    }
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
            double file_time = stopwatch->RealTime();
            stopwatch->Continue();
            
            fwlite::Event ev(in_file);
            for(ev.toBegin(); !ev.atEnd(); ++ev, ++ievt) {
                edm::EventBase const & event = ev;
                
                muon_cuts.initialize_branches();
                jet_cuts.initialize_branches();
                // break loop if maximal number of events is reached
                if(maxEvents_>0 ? ievt+1>maxEvents_ : false) break;
                
                if(outputEvery_!=0 ? (ievt>0 && ievt%outputEvery_==0) : false)
                    LogInfo << "  processing event: " << ievt << std::endl;
                
                bool passes_hlt_cuts = hlt_cuts.process(event);
                if(!passes_hlt_cuts) continue;
                
                bool passes_muon_cuts = muon_cuts.process(event);
                if(!passes_muon_cuts) continue;
                
                bool passes_veto_lepton_cuts = veto_lepton_cuts.process(event);
                if(!passes_veto_lepton_cuts) continue;
                
                bool passes_mt_mu_cuts = mt_mu_cuts.process(event);
                if(!passes_mt_mu_cuts) continue;
                
                bool passes_jet_cuts = jet_cuts.process(event);
                if(!passes_jet_cuts) continue;
                
                bool passes_tag_cuts = btag_cuts.process(event);
                if(!passes_tag_cuts) continue;
                
                bool passes_top_cuts = top_cuts.process(event);
                if(!passes_top_cuts) continue;
                
                misc_vars.process(event);
                if(weights.doWeights) weights.process(event);
                
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
            long count_events = 0;
            for(ls.toBegin(); !ls.atEnd(); ++ls) {
                edm::Handle<edm::MergeableCounter> counter;
                ls.getByLabel(totalPATProcessedCountSrc, counter);
                count_map["total_processed"] += counter->value;
            }
            in_file->Close();
            file_time = stopwatch->RealTime() - file_time;
            stopwatch->Continue();
            bytes_read += in_file->GetBytesRead();
            LogInfo << "Closing file " << in_file->GetPath() << " with " << in_file->GetBytesRead()/(1024*1024) << " Mb read, " << in_file->GetBytesRead()/(1024*1024) / file_time << " Mb/s" << std::endl;
        }
    }
    
    count_map["pass_hlt_cuts"] += hlt_cuts.n_pass;
    count_map["pass_lepton_cuts"] += muon_cuts.n_pass;
    count_map["pass_lepton_veto_cuts"] += veto_lepton_cuts.n_pass;
    count_map["pass_mt_cuts"] += mt_mu_cuts.n_pass;
    count_map["pass_jet_cuts"] += jet_cuts.n_pass;
    count_map["pass_btag_cuts"] += btag_cuts.n_pass;
    count_map["pass_top_cuts"] += top_cuts.n_pass;
    count_map["pass_gen_cuts"] += gen_particles.n_pass;
    
    int i = 1;
    for (auto& elem : count_map_order) {
        count_hist->AddBinContent(i, count_map[elem]);
        count_hist->GetXaxis()->SetBinLabel(i, elem.c_str());
        i++;
    }
    
    std::cout << "total processed step1 " << count_map["total_processed"] << std::endl;
    std::cout << "total processed step3 " << ievt << std::endl;
    std::cout << "hlt cuts " << hlt_cuts.toString() << std::endl;
    std::cout << "muon cuts " << muon_cuts.toString() << std::endl;
    std::cout << "veto lepton cuts " << veto_lepton_cuts.toString() << std::endl;
    std::cout << "mt_mu cuts " << mt_mu_cuts.toString() << std::endl;
    std::cout << "jet cuts " << jet_cuts.toString() << std::endl;
    std::cout << "tag cuts " << btag_cuts.toString() << std::endl;
    std::cout << "top cuts " << top_cuts.toString() << std::endl;
    std::cout << "gen cuts " << gen_particles.toString() << std::endl;
    stopwatch->Stop();
    
    double time = stopwatch->RealTime();
    int speed = (int)((float)ievt / time);
    LogInfo << "processing speed = " << speed << " events/sec" << std::endl;
    LogInfo << "read " << bytes_read/(1024*1024) << " Mb in total, average speed " << bytes_read/(1024*1024) / time << " Mb/s" << std::endl;  
    //    for (auto& elem : cut_count_map) {
    //        std::cout << elem.first << " " << elem.second << std::endl;
    //    }
    
    return 0;
}
