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
      const std::unique_ptr<std::map<const char*, TFormula>> SFs; 
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

//
// constructors and destructor
//
BTagSystematicsWeightProducer::BTagSystematicsWeightProducer(const edm::ParameterSet& iConfig)
: SFs(new std::map<const char*, TFormula>())
, effs(new std::map<const char*, double>())
, jetSrc(iConfig.getParameter<edm::InputTag>("src"))
, nJets(iConfig.getParameter<unsigned int>("nJets"))
, nTags(iConfig.getParameter<unsigned int>("nTags"))
{
   (*SFs)["b"] = TFormula("SFb", iConfig.getParameter<std::string>("SFb").c_str()); 
   (*SFs)["c"] = TFormula("SFc", iConfig.getParameter<std::string>("SFc").c_str()); 
   (*SFs)["l"] = TFormula("SFl", iConfig.getParameter<std::string>("SFl").c_str()); 
   
   (*SFsUp)["b"] = TFormula("SFbUp", iConfig.getParameter<std::string>("SFbUp").c_str()); 
   (*SFsUp)["c"] = TFormula("SFcUp", iConfig.getParameter<std::string>("SFcUp").c_str()); 
   (*SFsUp)["l"] = TFormula("SFlUp", iConfig.getParameter<std::string>("SFlUp").c_str()); 
   (*SFsDown)["b"] = TFormula("SFbDown", iConfig.getParameter<std::string>("SFbDown").c_str()); 
   (*SFsDown)["c"] = TFormula("SFcDown", iConfig.getParameter<std::string>("SFcDown").c_str()); 
   (*SFsDown)["l"] = TFormula("SFlDown", iConfig.getParameter<std::string>("SFlDown").c_str()); 
   
   (*effs)["b"] = iConfig.getParameter<double>("eff_b"); 
   (*effs)["c"] = iConfig.getParameter<double>("eff_c"); 
   (*effs)["l"] = iConfig.getParameter<double>("eff_l"); 

   //Precalculate the tagging combinations 
   combinations(nJets, nTags, combs);
 
   produces<float>("bTagWeight");
   produces<float>("bTagWeightSystBCUp");
   produces<float>("bTagWeightSystBCDown");
   produces<float>("bTagWeightSystLUp");
   produces<float>("bTagWeightSystLDown");
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
   Handle<View<pat::Jet> > jets;
   iEvent.getByLabel(jetSrc, jets);

   LogDebug("produce") << "This event has " << jets->size() << " jets";
   
   double P_mc = 0.0; 
   double P_data = 0.0;

   for(std::vector<unsigned int>& comb : combs) {

       unsigned int jetIdx = 0; 
       double p_mc = 1.0; 
       double p_data = 1.0; 
       for (const pat::Jet& jet : *jets) {
           bool inComb = std::find(comb.begin(), comb.end(), jetIdx) != comb.end();
           //bool inComb = false; 
           
           auto prob = [&, &p_mc, &p_data, inComb, jet, this] (const char* type) {
               
               auto eff = [] (double x, bool _inComb) -> double {
                   return _inComb ? x : 1.0 - x;
               };
               
               p_mc = p_mc * eff( ((*effs)[type]), inComb);
               p_data = p_data * eff( (*SFs)[type].Eval(jet.pt(), jet.eta())*((*effs)[type]), inComb);
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

           jetIdx++;
       }
      
       //Probabilities of different combinations add
       P_mc += p_mc;
       P_data += p_data;

   }
   double w = P_data/P_mc;
   std::auto_ptr<double> outW(new double(w));

   iEvent.put(outW, "bTagWeight");
 
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
