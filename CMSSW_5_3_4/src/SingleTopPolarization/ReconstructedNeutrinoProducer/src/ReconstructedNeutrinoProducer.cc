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

#include "CommonTools/UtilAlgos/interface/StringCutEventSelector.h"

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
      edm::InputTag metSrc;
      const std::string outName;

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
: outName("")
{
  leptonSrc = iConfig.getParameter<edm::InputTag>("leptonSrc");
  metSrc = iConfig.getParameter<edm::InputTag>("metSrc");

  produces<std::vector<reco::CompositeCandidate> >(outName);
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
   Handle<View<reco::Candidate> > mets;

   iEvent.getByLabel(leptonSrc, leptons);
   iEvent.getByLabel(metSrc, mets);


   std::auto_ptr<double> mtW(new double(0));

   std::auto_ptr<std::vector<reco::CompositeCandidate> > outNeutrinoColl(new std::vector<reco::CompositeCandidate>);
   reco::CompositeCandidate *nu = new reco::CompositeCandidate();
   std::unique_ptr<reco::CompositeCandidate::LorentzVector> nuVec(new reco::CompositeCandidate::LorentzVector(TMath::QuietNaN(), TMath::QuietNaN(),TMath::QuietNaN(),TMath::QuietNaN()));

   if(leptons->size()!=1 || mets->size()!=1) { //Need exactly 1 lepton and 1 MET
    edm::LogError("produce()") << "Event does not have correct final state for neutrino: nLeptons " << leptons->size() << " nMETs " << mets->size();
   }
   else {
    LogDebug("produce()") << "Event has correct final state for neutrino";

    const reco::Candidate& lepton(leptons->at(0));
    const reco::Candidate& MET(mets->at(0));

    float Lambda = TMath::Power(ReconstructedNeutrinoProducer::mW, 2) / 2 + lepton.p4().px()*MET.p4().px() + lepton.p4().py()*MET.p4().py();
    LogDebug("produce()") << "MET: px (" << MET.p4().Px() << ") py (" << MET.p4().Py() << ") pt (" << MET.p4().Pt() << ")";
    float Delta = TMath::Power(lepton.p4().E(), 2) * (TMath::Power(Lambda, 2) - TMath::Power(lepton.p4().Pt()*MET.p4().Pt(), 2) );
    float p_nu_z = TMath::QuietNaN();

    if(Delta>0.0) { //Real roots
      float r = TMath::Sqrt(Delta);
      float A = (Lambda*lepton.p4().Pz() + r)/ TMath::Power(lepton.p4().Pt(), 2);
      float B = (Lambda*lepton.p4().Pz() + r)/ TMath::Power(lepton.p4().Pt(), 2);
      p_nu_z = std::min(abs(A), abs(B)); //Choose root with minimal absolute value
    }
    else { //Negative discriminant, complex roots (MET resolution effect)
      LogDebug("produce()") << "Delta is negative, complex roots";
      float sk1 = lepton.p4().Pt()*MET.p4().Pt();
      float sk2 = MET.p4().Px()*lepton.p4().Px() + MET.p4().Py()*lepton.p4().Py();
      float mW_new = TMath::Sqrt(2*(sk1-sk2));
      LogDebug("produce()") << "Choosing new mW value to make Delta==0: mW_new=" << mW_new;
      float Lambda_new = TMath::Power(mW_new, 2) / 2.0 + sk2;
      //float Delta_new = (TMath::Power(Lambda_new, 2) - TMath::Power(sk1, 2))*TMath::Power(lepton.p4().E(), 2);
      p_nu_z = (Lambda_new*lepton.p4().Pz())/TMath::Power(lepton.p4().Pt(), 2);
    }
    float E_nu = TMath::Sqrt(TMath::Power(MET.p4().Pt(), 2) + TMath::Power(p_nu_z, 2));
    nuVec->SetPx(MET.p4().Px());
    nuVec->SetPy(MET.p4().Py());
    nuVec->SetPz(p_nu_z);
    nuVec->SetE(E_nu);
   }




   nu->setP4(*nuVec);
   outNeutrinoColl->push_back(*nu);

   LogDebug("produce()") << "neutrino: pt (" << nu->pt() << ") eta (" << nu->eta() << ") phi (" << nu->phi() << ") et (" << nu->et() << ")";
   iEvent.put(outNeutrinoColl, outName);

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
