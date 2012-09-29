// -*- C++ -*-
//
// Package:    ReconstructedNeutrinoProducer
// Class:      ReconstructedNeutrinoProducer
// 
/**\class ReconstructedNeutrinoProducer ReconstructedNeutrinoProducer.cc SingleTopPolarization/ReconstructedNeutrinoProducer/src/ReconstructedNeutrinoProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Wed Sep 26 16:21:03 EEST 2012
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

#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/Candidate/interface/Candidate.h> 
#include <DataFormats/RecoCandidate/interface/RecoCandidate.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>

#include "FWCore/MessageLogger/interface/MessageLogger.h"

#include "FWCore/Utilities/interface/InputTag.h"

class ReconstructedNeutrinoProducer : public edm::EDProducer {
   public:
      explicit ReconstructedNeutrinoProducer(const edm::ParameterSet&);
      ~ReconstructedNeutrinoProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
      static const float mW;


   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);


      edm::InputTag leptonSrc;
      edm::InputTag bjetSrc;
      edm::InputTag metSrc;

      // ----------member data ---------------------------
};
const float ReconstructedNeutrinoProducer::mW = 80.399;

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
ReconstructedNeutrinoProducer::ReconstructedNeutrinoProducer(const edm::ParameterSet& iConfig)
{
  leptonSrc = iConfig.getParameter<edm::InputTag>("leptonSrc");
  bjetSrc = iConfig.getParameter<edm::InputTag>("bjetSrc");
  metSrc = iConfig.getParameter<edm::InputTag>("metSrc");

  produces<std::vector<reco::CompositeCandidate> >();
   //register your products
/* Examples
   produces<ExampleData2>();

   //if do put with a label
   produces<ExampleData2>("label");
 
   //if you want to put into the Run
   produces<ExampleData2,InRun>();
*/
   //now do what ever other initialization is needed
  
}


ReconstructedNeutrinoProducer::~ReconstructedNeutrinoProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
ReconstructedNeutrinoProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;

   Handle<View<reco::Candidate> > leptons;
   Handle<View<reco::Candidate> > bjets;
   Handle<View<reco::Candidate> > mets;

   iEvent.getByLabel(leptonSrc, leptons);
   iEvent.getByLabel(bjetSrc, bjets);
   iEvent.getByLabel(metSrc, mets);

   std::auto_ptr<std::vector<reco::CompositeCandidate> > outNeutrinoColl(new std::vector<reco::CompositeCandidate>);
   reco::CompositeCandidate *nu = new reco::CompositeCandidate();

   reco::CompositeCandidate::LorentzVector *nuVec = new reco::CompositeCandidate::LorentzVector(TMath::QuietNaN(), TMath::QuietNaN(),TMath::QuietNaN(),TMath::QuietNaN());

   nu->setP4(*nuVec);
   outNeutrinoColl->push_back(*nu);

   LogDebug("produced neutrino") << "pt " << nu->pt() << " eta " << nu->eta() << " phi " << nu->phi();
   iEvent.put(outNeutrinoColl);


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
ReconstructedNeutrinoProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
ReconstructedNeutrinoProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
ReconstructedNeutrinoProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
ReconstructedNeutrinoProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
ReconstructedNeutrinoProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
ReconstructedNeutrinoProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
ReconstructedNeutrinoProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(ReconstructedNeutrinoProducer);
