// -*- C++ -*-
//
// Package:    CandTransverseMassProducer
// Class:      CandTransverseMassProducer
// 
/**\class CandTransverseMassProducer CandTransverseMassProducer.cc SingleTopPolarization/CandTransverseMassProducer/src/CandTransverseMassProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Mon Oct  1 17:15:15 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>


//
// class declaration
//

class CandTransverseMassProducer : public edm::EDProducer {
   public:
      explicit CandTransverseMassProducer(const edm::ParameterSet&);
      ~CandTransverseMassProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

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
CandTransverseMassProducer::CandTransverseMassProducer(const edm::ParameterSet& iConfig)
{
   //register your products
   produces<double>();
   //now do what ever other initialization is needed
  
}


CandTransverseMassProducer::~CandTransverseMassProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
CandTransverseMassProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<reco::Candidate> cands1;
   //iEvent.getByLabel(candSrc, pIn);

   // std::vector<reco::Candidate::LorentzVector*> vecs;

   // for(auto& c : *cands1) {
   //  vecs->push_back(*(c.p4()));
   // }


/* This is an event example
   //Read 'ExampleData' from the Event
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);

   //Use the ExampleData to create an ExampleData2 which 
   // is put into the Event
   std::auto_ptr<ExampleData2> pOut(new ExampleData2(*pIn));
   iEvent.put(pOut);
*/

/* this is an EventSetup example
   //Read SetupData from the SetupRecord in the EventSetup
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
*/
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
CandTransverseMassProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CandTransverseMassProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
CandTransverseMassProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CandTransverseMassProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CandTransverseMassProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CandTransverseMassProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CandTransverseMassProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CandTransverseMassProducer);
