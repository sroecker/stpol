// -*- C++ -*-
//
// Package:    EfficiencyAnalyzer
// Class:      EfficiencyAnalyzer
// 
/**\class EfficiencyAnalyzer EfficiencyAnalyzer.cc test/EfficiencyAnalyzer/src/EfficiencyAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
//         Created:  Tue Sep 11 21:15:04 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

//Required for accessing the lumi-block counters
#include "DataFormats/Common/interface/MergeableCounter.h"

//Required for TFileService
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

//
// class declaration
//

class EfficiencyAnalyzer : public edm::EDAnalyzer {
   public:
      explicit EfficiencyAnalyzer(const edm::ParameterSet&);
      ~EfficiencyAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      // ----------member data ---------------------------
      edm::Service<TFileService> fs;

      unsigned long processedEventCounter;
      unsigned long passedEventCounter;

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
EfficiencyAnalyzer::EfficiencyAnalyzer(const edm::ParameterSet& iConfig)

{
   processedEventCounter = 0;
   passedEventCounter = 0;

}


EfficiencyAnalyzer::~EfficiencyAnalyzer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
EfficiencyAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;



#ifdef THIS_IS_AN_EVENT_EXAMPLE
   Handle<ExampleData> pIn;
   iEvent.getByLabel("example",pIn);
#endif
   
#ifdef THIS_IS_AN_EVENTSETUP_EXAMPLE
   ESHandle<SetupData> pSetup;
   iSetup.get<SetupRecord>().get(pSetup);
#endif
}


// ------------ method called once each job just before starting event loop  ------------
void 
EfficiencyAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
EfficiencyAnalyzer::endJob() 
{
    double efficiency = (double)passedEventCounter / (double)processedEventCounter;
    std::cout << "processedEventCounter = " << processedEventCounter << std::endl;
    std::cout << "passedEventCounter = " << passedEventCounter << std::endl;
    std::cout << "efficiency = " << std::scientific << efficiency << std::endl;
}

// ------------ method called when starting to processes a run  ------------
void 
EfficiencyAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
EfficiencyAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
EfficiencyAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
EfficiencyAnalyzer::endLuminosityBlock(const edm::LuminosityBlock& lumi, edm::EventSetup const&)
{
    edm::Handle<edm::MergeableCounter> counter;
    lumi.getByLabel("processedEventCounter", counter);
    processedEventCounter += (unsigned long)(counter->value);
    lumi.getByLabel("passedEventCounter", counter);
    passedEventCounter += (unsigned long)(counter->value);
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
EfficiencyAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(EfficiencyAnalyzer);
