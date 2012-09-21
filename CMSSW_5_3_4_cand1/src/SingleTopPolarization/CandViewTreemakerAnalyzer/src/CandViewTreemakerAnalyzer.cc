// -*- C++ -*-
//
// Package:    CandViewTreemakerAnalyzer
// Class:      CandViewTreemakerAnalyzer
// 
/**\class CandViewTreemakerAnalyzer CandViewTreemakerAnalyzer.cc SingleTopPolarization/CandViewTreemakerAnalyzer/src/CandViewTreemakerAnalyzer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  
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

#include "TTree.h"

//for ITOA
#include <sstream>

//
// class declaration
//

#define ITOA(A) (static_cast<std::ostringstream*>(&(std::ostringstream()<<A) )->str())
#define D_NAN (std::numeric_limits<double>::quiet_NaN())

class CandViewTreemakerAnalyzer : public edm::EDAnalyzer {
   public:
      explicit CandViewTreemakerAnalyzer(const edm::ParameterSet&);
      ~CandViewTreemakerAnalyzer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      /*
      This is a map that stores as the key the name of an object collection,
      such as 'selectedPatMuons' and as value the variables to get from that
      collection. The variables are stored as another map, where the key is the
      name of that variable that will end up in the TTree and the value is a
      StringObjectFunction that allows the variable to be extracted from the
      collection.
      */
      std::map<std::string, std::map<std::string, StringObjectFunction<reco::Candidate>*>> quantities;

      std::map<std::string, std::map<std::string, std::vector<double*>>> treeValues;
      std::map<std::string, int> maxElems;

      edm::Service<TFileService> fs;

      TTree* outTree;
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
CandViewTreemakerAnalyzer::CandViewTreemakerAnalyzer(const edm::ParameterSet& iConfig)

{
  outTree = fs->make<TTree>("eventTree", "eventTree");

  auto collectionsPSets = iConfig.getUntrackedParameter<std::vector<edm::ParameterSet>>("collections");
  for (auto& colPSet : collectionsPSets) {
    const auto& collection = colPSet.getUntrackedParameter<std::string>("collection");
    maxElems[collection] = colPSet.getUntrackedParameter<int>("maxElems");
    const auto& varPSets = colPSet.getUntrackedParameter<std::vector<edm::ParameterSet>>("variables");
    for (auto& varPSet : varPSets) {
      const auto& tag = varPSet.getUntrackedParameter<std::string>("tag");
      const auto& expr = varPSet.getUntrackedParameter<std::string>("expr");
      quantities[collection][tag] = new StringObjectFunction<reco::Candidate>(expr, false);
      for(int i=0;i<maxElems[collection];i++) {
        double* d = new double(D_NAN);
        treeValues[collection][tag].push_back(d);
        const std::string brName = collection + "_" + ITOA(i) + "_" + tag;
        outTree->Branch(brName.c_str(), d);
      }
    }
  }  
}


CandViewTreemakerAnalyzer::~CandViewTreemakerAnalyzer()
{
  for(auto& collectionVarMap : quantities) {
    auto& varMap = collectionVarMap.second;
    for (auto& var : varMap) {
      delete var.second;
    }
  }


  for(auto& colLevel : treeValues) {
    for (auto& varLevel : colLevel.second) {
      for (auto& d : varLevel.second) {
        delete d;
      }
    }
  }

}


//
// member functions
//

// ------------ method called for each event  ------------
void
CandViewTreemakerAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  //std::cout << "Begin processing event" << std::endl;

  using namespace edm;

  Handle<edm::View<reco::Candidate>> objects;

  //Initialize all branch variables
  for (auto& cols : treeValues) {
    for (auto& value : cols.second) {
      //std::cout << cols.first << " " << value.first << " " << value.second.size() << std::endl;
      for(auto& v : value.second) {
        *v = D_NAN;
      }
    }
  }

  for (auto& collection : quantities) {
    auto& collectionName = collection.first;
    iEvent.getByLabel(collectionName, objects);

    auto& varMap = collection.second;

    int i = 0; //count the objects of the collection of interest
    for (auto& obj : *objects) {
      for (auto& var : varMap) {
        auto& tag = var.first;
        auto& varParser = *(var.second);
        const double&& value = varParser(obj);
        //std::cout << collectionName << "[" << i << "] " << tag << " " << value << std::endl;
        if (i<maxElems[collectionName]) {
          *(treeValues[collectionName][tag][i]) = value;
        }
      }
      i++;
    }
  }

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
void 
CandViewTreemakerAnalyzer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
CandViewTreemakerAnalyzer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
CandViewTreemakerAnalyzer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
CandViewTreemakerAnalyzer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
CandViewTreemakerAnalyzer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
CandViewTreemakerAnalyzer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
CandViewTreemakerAnalyzer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  //edm::ParameterSetDescription desc;
  //desc.setUnknown();
  //descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(CandViewTreemakerAnalyzer);
