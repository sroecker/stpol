// -*- C++ -*-
//
// Package:    BTagSystematicsWeightProducer
// Class:      BTagSystematicsWeightProducer
// 
/**\class BTagSystematicsWeightProducer BTagSystematicsWeightProducer.cc SingleTopPolarization/BTagSystematicsWeightProducer/src/BTagSystematicsWeightProducer.cc

 Description: Produces the b-tag reweight from the b-tagging efficiency and the scale factor, along with the up/down variation of this weight.

 Implementation:
     
*/
//
// Original Author:  Joosep Pata
//         Created:  Fri Dec 21 16:47:11 EET 2012
// $Id$
//
//


// system include files
#include <memory>
#include <algorithm>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include <TFormula.h>
#include <TH1D.h>


//
// class declaration
//

typedef std::vector<std::vector<unsigned int>> Combinations;

class BTagSystematicsWeightProducer : public edm::EDProducer {
   public:
      explicit BTagSystematicsWeightProducer(const edm::ParameterSet&);
      ~BTagSystematicsWeightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);


      void combinations(const unsigned int n, const unsigned int k, Combinations& combs);
      
      
      const std::unique_ptr<std::map<const char*, TFormula>> SFs; 
      const std::unique_ptr<std::map<const char*, TH1D>> SFErrs; 
      const std::unique_ptr<std::map<const char*, double>> effs; 
      const edm::InputTag jetSrc;
      const unsigned int nJets, nTags; 
      Combinations combs;

      // ----------member data ---------------------------
};

//
// constants, enums and typedefs
//


//
// static data member definitions
//
TH1D prepareErrHist(const char* name, std::vector<Double_t> bins, std::vector<Double_t> errs) {
   assert(bins.size() == errs.size()+1);
   TH1D h(name, name, bins.size()-1, &bins[0]);
   for(unsigned int i=0;i<errs.size();i++) {
     h.SetBinContent(i, errs[i]); 
   }

   {
       std::stringstream os;
       os << "(";
       for(int i=1;i<=h.GetNbinsX();i++) {
         os << i << ":" << "{" << h.GetBinLowEdge(i) << "," << h.GetBinContent(i) << "}, "; 
       }
       os << ")";
       LogDebug("constructor") << name << " error histogram:" << os.str();
   }
   return h;   
}
//
// constructors and destructor
//
BTagSystematicsWeightProducer::BTagSystematicsWeightProducer(const edm::ParameterSet& iConfig)
: SFs(new std::map<const char*, TFormula>())
, effs(new std::map<const char*, double>())
, SFErrs(new std::map<const char*, TH1D>())
, jetSrc(iConfig.getParameter<edm::InputTag>("src"))
, nJets(iConfig.getParameter<unsigned int>("nJets"))
, nTags(iConfig.getParameter<unsigned int>("nTags"))
{
   (*SFs)["b"] = TFormula("SFb", iConfig.getParameter<std::string>("SFb").c_str()); 
   (*SFs)["c"] = TFormula("SFc", iConfig.getParameter<std::string>("SFc").c_str()); 
   (*SFs)["l"] = TFormula("SFl", iConfig.getParameter<std::string>("SFl").c_str()); 
  
   (*SFErrs)["c"] = prepareErrHist("SFcErr",
                                   iConfig.getParameter<std::vector<double>>("SFcErrBinsX"),
                                   iConfig.getParameter<std::vector<double>>("SFcErrBinsY")
   ); 
   (*SFErrs)["b"] = prepareErrHist("SFbErr",
                                   iConfig.getParameter<std::vector<double>>("SFbErrBinsX"),
                                   iConfig.getParameter<std::vector<double>>("SFbErrBinsY")
   ); 
   (*SFErrs)["l"] = prepareErrHist("SFlErr",
                                   iConfig.getParameter<std::vector<double>>("SFlErrBinsX"),
                                   iConfig.getParameter<std::vector<double>>("SFlErrBinsY")
   ); 
   
   (*effs)["b"] = iConfig.getParameter<double>("Effb"); 
   (*effs)["c"] = iConfig.getParameter<double>("Effc"); 
   (*effs)["l"] = iConfig.getParameter<double>("Effl"); 

   //Precalculate the tagging combinations 
   combinations(nJets, nTags, combs);
 
   produces<double>("bTagWeight");
   produces<double>("bTagWeightSystBCUp");
   produces<double>("bTagWeightSystBCDown");
   produces<double>("bTagWeightSystLUp");
   produces<double>("bTagWeightSystLDown");
}

void BTagSystematicsWeightProducer::combinations(const unsigned int n, const unsigned int k, Combinations& combs) {
    std::vector<bool> v(n);
    std::fill(v.begin()+v.size()-k, v.end(), true);
    do {
        std::vector<unsigned int> comb;
        for(unsigned int i=0;i<v.size();i++) {
            if(v[i])
                comb.push_back(i);
        }
        combs.push_back(comb);
    }
    while(std::next_permutation(v.begin(), v.end()));
    std::reverse(combs.begin(), combs.end()); 
}


BTagSystematicsWeightProducer::~BTagSystematicsWeightProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
BTagSystematicsWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<View<reco::Candidate>> jets;
   iEvent.getByLabel(jetSrc, jets);

   //std::vector<pat::Jet> interestingJets(jets.begin(),jets.begin() + nJets);
   LogDebug("produce") << "This event has " << jets->size() << " jets";
   
   double P_mc = 0.0; 
   double P_data = 0.0;

   for(std::vector<unsigned int>& comb : combs) {
       
       std::stringstream os; for(auto& v : comb) { os << " " << v; };

       LogDebug("produce") << " considering jets:" << os.str() << " as b-tags";
      
       unsigned int jetIdx = 0; 
       double p_mc = 1.0; 
       double p_data = 1.0;



       for (const auto& jet_ : *jets) {
           
           pat::Jet& jet = (pat::Jet&)jet_;

           bool inComb = std::find(comb.begin(), comb.end(), jetIdx) != comb.end();
           //bool inComb = false; 
           
           auto prob = [&, &p_mc, &p_data, inComb, jet, this] (const char* type) {
               
               auto eff = [] (double x, bool _inComb) -> double {
                   return _inComb ? x : 1.0 - x;
               };
               
               p_mc = p_mc * eff( ((*effs)[type]), inComb);
               p_data = p_data * eff( (*SFs)[type].Eval(jet.pt())*((*effs)[type]), inComb);
           };
 
           if(abs(jet.partonFlavour()) == 5) { //b-jet
               prob("b"); //multiply the probability corresponding to the b-jet 
           }
           else if(abs(jet.partonFlavour())==4) { //c-jet
               prob("c"); 
           }
           else if(abs(jet.partonFlavour())==21 || abs(jet.partonFlavour())<=3) { //light jet
               prob("l"); 
           }
           LogDebug("produce") << "comb probs: p_mc=" << p_mc << " p_data=" << p_data;

           jetIdx++;
       }
      
       //Probabilities of different combinations add
       P_mc += p_mc;
       P_data += p_data;

   }
   double w = P_data/P_mc;
 //  std::auto_ptr<double> outW(new double(w));
   LogDebug("produce") << "event prob: P_mc=" << P_mc << " P_data=" << P_data << " w=" << w;
   iEvent.put(std::auto_ptr<double>(new double(w)), "bTagWeight");
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
BTagSystematicsWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
BTagSystematicsWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
BTagSystematicsWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
BTagSystematicsWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
BTagSystematicsWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
BTagSystematicsWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
BTagSystematicsWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BTagSystematicsWeightProducer);
