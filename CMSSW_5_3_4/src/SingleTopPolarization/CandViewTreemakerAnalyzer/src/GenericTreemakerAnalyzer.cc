// -*- C++ -*-
//
// Package:    GenericTreemakerAnalyzer
// Class:      GenericTreemakerAnalyzer
// 
/**\class GenericTreemakerAnalyzerGenericTreemakerAnalyzer GenericTreemakerAnalyzer.cc SingleTopPolarization/GenericTreemakerAnalyzer/src/GenericTreemakerAnalyzer.cc

 Description: This class produces a TTree, the branches of which are the specified components of given collections

 Implementation:
     This class is implemented using the StringObjectFunction to allow generic
     object properties to be outputted to the TTree. All configuration is done
     via the python interface. The first template argument T is a collection
     type object which must be present in the file. A typical value for T
     is edm::View<reco::Candidate> or reco::CandidateCollection (aka OwnVector).

     The objects in the collection are treated as instances of the class C, meaning
     that T::value_type must be a base type of C. A typical value for C is
     pat::Jet if you wish to access the jet properties of an object.
*/
//
// Original Author: Joosep Pata
//         Created:  Fri Sep 21 11:28:31 EEST 2012
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

//Required for reco::Candidate
#include <DataFormats/Candidate/interface/Candidate.h> 

//Required for StringObjectFunction
#include <CommonTools/Utils/interface/StringObjectFunction.h>

//Required for TFileService
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "CommonTools/UtilAlgos/interface/SingleObjectSelector.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"

#include "TTree.h"
#include <TMath.h>
     
//for ITOA
#include <sstream>

#include "FWCore/MessageLogger/interface/MessageLogger.h"


//
// class declaration
//

#define ITOA(A) (static_cast<std::ostringstream*>(&(std::ostringstream()<<A) )->str())
#define D_NAN (std::numeric_limits<double>::quiet_NaN())

template <typename T>
class GenericTreemakerAnalyzer : public edm::EDAnalyzer {
   public:
      explicit GenericTreemakerAnalyzer(const edm::ParameterSet&);
      ~GenericTreemakerAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

      static const T defaultValue;


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      //All the branch variables
      std::map<std::string, T*> treeValues;
      std::map<std::string, edm::InputTag> colNames;

      //Maximum number of elements per collection
      //std::map<std::string, int> maxElems;

      edm::Service<TFileService> fs;

      TTree* outTree;

      bool makeTree;
      std::string treeName;

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
GenericTreemakerAnalyzer<T>::GenericTreemakerAnalyzer(const edm::ParameterSet& iConfig)
{

  makeTree = iConfig.getUntrackedParameter<bool>("makeTree", true);
  treeName = iConfig.getUntrackedParameter<std::string>("treeName", "eventTree");

  if(makeTree) {
    outTree = fs->make<TTree>(treeName.c_str(), treeName.c_str());
  } else {
    outTree = fs->getObject<TTree>(treeName.c_str());
  }

  auto collectionsPSets = iConfig.getParameter<std::vector<edm::InputTag>>("collections");
  for (auto& colTag : collectionsPSets) {
    treeValues[colTag.encode()] = new T();
    std::string brName = colTag.instance() + std::string("_") + colTag.label();
    colNames[colTag.encode()] = colTag;
    outTree->Branch(brName.c_str(), treeValues[colTag.encode()]);
  }
}


template <typename T>
GenericTreemakerAnalyzer<T>::~GenericTreemakerAnalyzer()
{
}


//
// member functions
//

// ------------ method called for each event  ------------
template <typename T>
void
GenericTreemakerAnalyzer<T>::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  //std::cout << "Begin processing event" << std::endl;

  using namespace edm;


  //Initialize all branch variables
  for (auto& cols : treeValues) {
    *(cols.second) = defaultValue;
  }

  for (auto& cols : colNames) {
    Handle<T> object;
    iEvent.getByLabel(cols.second, object);
    if(object.isValid()) {
      LogDebug("produce()") << "Collection " << cols.second.encode()  << " = " << *object;
      *(treeValues[cols.first]) = *object;
    } else {
      LogError("produce()") << "Collection " << cols.second.encode() << " is not available";
    }

  }

  // for (auto& collection : quantities) {
  //   auto& collectionName = collection.first;
  //   iEvent.getByLabel(collectionName, objects);

  //   auto& varMap = collection.second;

  //   //std::cout << "col " << collectionName << " " << objects->size() << std::endl;

  //   int i = 0; //count the objects of the collection of interest
  //   if(objects.isValid() ) {
  //     for (auto& obj : *objects) {
  //       //std::cout << "obj ";
  //       for (auto& var : varMap) {
  //         auto& tag = var.first;
  //         //std::cout << "var(" << tag << ") ";
  //         auto& varParser = *(var.second);
  //         //const double value = varParser((pat::Jet)(obj));
  //         const C* pObj = static_cast<const C*>(&obj);
  //         if (pObj == 0) {
  //           std::cout << "Could not cast" << std::endl;
  //         }
  //         const double&& value = varParser(*pObj);
  //         //std::cout << value << " ";
  //         //std::cout << collectionName << "[" << i << "] " << tag << " " << value << std::endl;
  //         if (i<maxElems[collectionName]) {
  //           *(treeValues[collectionName][tag][i]) = value;
  //         } else {
  //           break;
  //         }
  //       }
  //       //std::cout << std::endl;
  //       i++;
  //     }
  //   } else { //
  //     LogDebug("produce()") << "Collection " << collectionName << " does not exist in event";
  //   }
  // }

  /*
  for (auto& cols : treeValues) {
    std::cout << cols.first << " ";
    for (auto& value : cols.second) {
      std::cout << value.first << " ";
      for(auto& v : value.second) {
        std::cout << *v << " ";
      }
    }
    std::cout << std::endl;
  }
  */
  
  outTree->Fill();
  //std::cout << "Done processing event" << std::endl;
}


// ------------ method called once each job just before starting event loop  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
template <typename T>
void 
GenericTreemakerAnalyzer<T>::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
template <typename T>
void
GenericTreemakerAnalyzer<T>::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

// typedef SingleObjectSelector<edm::View<pat::Jet>,
// StringCutObjectSelector< pat::Jet>,
// edm::OwnVector<pat::Jet, edm::ClonePolicy<pat::Jet>> > JetViewSelector;

//typedef SingleObjectSelector< edm::View<pat::Jet>, StringCutObjectSelector<pat::Jet, true>, edm::OwnVector<pat::Jet, edm::ClonePolicy<pat::Jet>> > JetViewSelector;

typedef GenericTreemakerAnalyzer<double> DoubleTreemakerAnalyzer;
template<> const double DoubleTreemakerAnalyzer::defaultValue = TMath::QuietNaN();

//define this as a plug-in
DEFINE_FWK_MODULE(DoubleTreemakerAnalyzer);

