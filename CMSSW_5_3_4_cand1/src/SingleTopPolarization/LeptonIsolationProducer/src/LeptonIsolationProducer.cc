// -*- C++ -*-
//
// Package:    LeptonIsolationProducer<T>
// Class:      LeptonIsolationProducer<T>
// 
/**\class LeptonIsolationProducer<T> LeptonIsolationProducer<T>.cc SingleTopPolarization/LeptonIsolationProducer<T>/src/LeptonIsolationProducer<T>.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue Sep 25 09:10:09 EEST 2012
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

#include "FWCore/Utilities/interface/InputTag.h"

//PAT
#include <DataFormats/PatCandidates/interface/Muon.h>
#include <DataFormats/PatCandidates/interface/Electron.h>



//
// class declaration
//
template <typename T>
class LeptonIsolationProducer : public edm::EDProducer {
   public:
      explicit LeptonIsolationProducer(const edm::ParameterSet&);
      ~LeptonIsolationProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

      edm::InputTag leptonSource;
      edm::InputTag rhoSource;

      float dR;


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
template <typename T>
LeptonIsolationProducer<T>::LeptonIsolationProducer(const edm::ParameterSet& iConfig)
{
   //register your products
/* Examples
   produces<ExampleData2>();

   //if do put with a label
   produces<ExampleData2>("label");
 
   //if you want to put into the Run
   produces<ExampleData2,InRun>();
*/
   produces<std::vector<T> >();

   leptonSource = iConfig.getParameter<edm::InputTag>("leptonSrc");
   rhoSource = iConfig.getParameter<edm::InputTag>("rhoSrc");
   dR = iConfig.getUntrackedParameter<double>("dR", 0.4);
   //now do what ever other initialization is needed
  
}


template <typename T>
LeptonIsolationProducer<T>::~LeptonIsolationProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
template <typename T>
void
LeptonIsolationProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  using namespace edm;

  Handle<std::vector<T> > leptons;
  Handle<double> rho;

  iEvent.getByLabel(leptonSource,leptons);
  iEvent.getByLabel(rhoSource,rho);

  std::auto_ptr<std::vector<T> > outLeptons(new std::vector<T>(*leptons));

  for (auto& lepton : *outLeptons) {
    float dbc_iso = (lepton.chargedHadronIso() + std::max(0., lepton.neutralHadronIso() + lepton.photonIso() - 0.5*lepton.puChargedHadronIso()))/lepton.et();
    double e = TMath::Pi() * dR * dR * (*rho);
    float rc_iso = (lepton.chargedHadronIso() + std::max(0., lepton.neutralHadronIso() + lepton.photonIso() - e))/lepton.et();
    lepton.addUserFloat("deltaBetaCorrRelIso", dbc_iso);
    lepton.addUserFloat("rhoCorrRelIso", rc_iso);
  }
  iEvent.put(outLeptons);

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
template <typename T>
void 
LeptonIsolationProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void 
LeptonIsolationProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void 
LeptonIsolationProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void 
LeptonIsolationProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void 
LeptonIsolationProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void 
LeptonIsolationProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
LeptonIsolationProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
typedef LeptonIsolationProducer<pat::Muon> MuonIsolationProducer;
typedef LeptonIsolationProducer<pat::Electron> ElectronIsolationProducer;
DEFINE_FWK_MODULE(MuonIsolationProducer);
DEFINE_FWK_MODULE(ElectronIsolationProducer);
