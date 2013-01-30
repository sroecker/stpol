// -*- C++ -*-
//
// Package:    PatObjectOwnRefProducer<T>
// Class:      PatObjectOwnRefProducer<T>
//
/**\class PatObjectOwnRefProducer<T> PatObjectOwnRefProducer.cc SingleTopPolarization/PatObjectOwnRefProducer/src/PatObjectOwnRefProducer.cc
 
 Description: [one line class summary]
 
 Implementation:
 [Notes on implementation]
 */
//
// Original Author:  Joosep Pata
//         Created:  Wed Jan 30 09:28:16 EET 2013
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
#include <DataFormats/PatCandidates/interface/Jet.h>
#include "FWCore/Utilities/interface/InputTag.h"


//
// class declaration
//
template <typename T>
class PatObjectOwnRefProducer : public edm::EDProducer {
public:
    explicit PatObjectOwnRefProducer(const edm::ParameterSet&);
    ~PatObjectOwnRefProducer();
    
    static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);
    
private:
    virtual void beginJob() ;
    virtual void produce(edm::Event&, const edm::EventSetup&);
    virtual void endJob() ;
    
    virtual void beginRun(edm::Run&, edm::EventSetup const&);
    virtual void endRun(edm::Run&, edm::EventSetup const&);
    virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
    
    const edm::InputTag src;
    
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
PatObjectOwnRefProducer<T>::PatObjectOwnRefProducer(const edm::ParameterSet& iConfig)
: src(iConfig.getParameter<edm::InputTag>("src"))
{
    produces<std::vector<T>>();
}


template <typename T>
PatObjectOwnRefProducer<T>::~PatObjectOwnRefProducer()
{
}

template <typename T>
void
PatObjectOwnRefProducer<T>::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
    using namespace edm;
    
    Handle<std::vector<T>> inColl;
    iEvent.getByLabel(src, inColl);
    
    /*if(! inColl.isValid()) {
        throw new 
    }*/
    
    std::auto_ptr<std::vector<T>> outColl(new std::vector<T>(*inColl));
    
    unsigned int i = 0;
    for( auto & elem : *outColl) {
        edm::Ref<View<T>> r(inColl, i);
        elem.addUserData("original", r);
        i++;
    }
    
    /*
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
PatObjectOwnRefProducer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endJob() {
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
PatObjectOwnRefProducer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
    //The following says we do not know what parameters are allowed so do no validation
    // Please change this to state exactly what you do use, even if it is no parameters
    edm::ParameterSetDescription desc;
    desc.setUnknown();
    descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PatObjectOwnRefProducer<pat::Jet>);
