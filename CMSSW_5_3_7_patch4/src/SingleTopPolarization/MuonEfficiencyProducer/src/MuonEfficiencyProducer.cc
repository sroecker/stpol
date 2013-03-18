// -*- C++ -*-
//
// Package:    MuonEfficiencyProducer
// Class:      MuonEfficiencyProducer
// 
/**\class MuonEfficiencyProducer MuonEfficiencyProducer.cc SingleTopPolarization/MuonEfficiencyProducer/src/MuonEfficiencyProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andres Tiko
//         Created:  R märts  8 18:40:17 EET 2013
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

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <DataFormats/PatCandidates/interface/Muon.h>

//
// class declaration
//

class MuonEfficiencyProducer : public edm::EDProducer {
   public:
      explicit MuonEfficiencyProducer(const edm::ParameterSet&);
      ~MuonEfficiencyProducer();

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
      const edm::InputTag src;
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
MuonEfficiencyProducer::MuonEfficiencyProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
{
   produces<double>("muonIDWeight");
   produces<double>("muonIDWeightUp");
   produces<double>("muonIDWeightDown");
   produces<double>("muonIsoWeight");
   produces<double>("muonIsoWeightUp");
   produces<double>("muonIsoWeightDown");   
}


MuonEfficiencyProducer::~MuonEfficiencyProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
MuonEfficiencyProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   double weightID = TMath::QuietNaN();
   double weightIDUp = TMath::QuietNaN();
   double weightIDDown = TMath::QuietNaN();
   double weightIso = TMath::QuietNaN();
   double weightIsoUp = TMath::QuietNaN();
   double weightIsoDown = TMath::QuietNaN();

   Handle<View<reco::Candidate> > muons;
   iEvent.getByLabel(src, muons);

   for ( uint i = 0; i < muons->size(); ++i ) {
      const pat::Muon& muon = (pat::Muon&)muons->at(i);
   
      LogDebug("eta ") << muon.eta() << std::endl;
      LogDebug("iso ") << muon.userFloat("deltaBetaCorrRelIso") << std::endl;
      
      if(abs(muon.eta())<0.9){
         weightID = 0.9939;
         weightIDUp = weightID + 0.0002;
         weightIDDown = weightID - 0.0002;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12  || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0004;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 0.9999;
            weightIsoUp = weightIso + 0.0001;
            weightIsoDown = weightIso - 0.0001;
         }
      }
      else if (abs(muon.eta()) < 1.2){
         weightID = 0.9902;
         weightIDUp = weightID + 0.0003;
         weightIDDown = weightID - 0.0003;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12 || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0031;
            weightIsoUp = weightIso + 0.0003;
            weightIsoDown = weightIso - 0.0003;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 1.0013;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }
      }
      else if(abs(muon.eta())<2.1){
         weightID = 0.9970;
         weightIDUp = weightID + 0.0003;
         weightIDDown = weightID - 0.0003;
         if(muon.userFloat("deltaBetaCorrRelIso")<0.12 || muon.userFloat("deltaBetaCorrRelIso")>0.2){
            weightIso = 1.0050;
            weightIsoUp = weightIso + 0.0002;
            weightIsoDown = weightIso - 0.0002;
         }else if(muon.userFloat("deltaBetaCorrRelIso")<0.2){
            weightIso = 1.0023;
            weightIsoUp = weightIso + 0.0001;
            weightIsoDown = weightIso - 0.0001;
         }
      }

      
   }

   

   LogDebug("Muon with id weights") << weightID << weightIDUp << weightIDDown;
   
   /*
   //tight
   abs(eta)<0.9 -> sf = 0.9939+-0.0002
   0.9<abs(eta)<1.2 -> 0.9902+-0.0003
   1.2<abs(eta)<2.1 -> 0.9970+-0.0003
   //loose
   A+B
   abs(eta)<0.9 -> sf = 0.9988+-0.0002
   0.9<abs(eta)<1.2 -> 0.9993+-0.0005
   1.2<abs(eta)<2.1 -> 0.9982+-0.0002
   C+D
   abs(eta)<0.9 -> sf = 0.9985+-0.0001
   0.9<abs(eta)<1.2 -> 0.9988+-0.0002
   1.2<abs(eta)<2.1 -> 0.9984+-0.0001

   ____
   PFComb dBeta RelIso <0.12
   abs(eta)<0.9 -> sf = 1.0004+-0.0002
   0.9<abs(eta)<1.2 -> 1.0031+-0.0003
   1.2<abs(eta)<2.1 -> 1.0050+-0.0002

   PFComb dBeta RelIso <0.2
   abs(eta)<0.9 -> sf = 0.9999+-0.0001
   0.9<abs(eta)<1.2 -> 1.0013+-0.0002
   1.2<abs(eta)<2.1 -> 1.0023+-0.0001

   */
   iEvent.put(std::auto_ptr<double>(new double(weightID)), "muonIDWeight");
   iEvent.put(std::auto_ptr<double>(new double(weightIDUp)), "muonIDWeightUp");
   iEvent.put(std::auto_ptr<double>(new double(weightIDDown)), "muonIDWeightDown");
   iEvent.put(std::auto_ptr<double>(new double(weightIso)), "muonIsoWeight");
   iEvent.put(std::auto_ptr<double>(new double(weightIsoUp)), "muonIsoWeightUp");
   iEvent.put(std::auto_ptr<double>(new double(weightIsoDown)), "muonIsoWeightDown");
}

// ------------ method called once each job just before starting event loop  ------------
void 
MuonEfficiencyProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
MuonEfficiencyProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
MuonEfficiencyProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
MuonEfficiencyProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
MuonEfficiencyProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
MuonEfficiencyProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
MuonEfficiencyProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(MuonEfficiencyProducer);
