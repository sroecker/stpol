#include <memory>
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include <CommonTools/UtilAlgos/interface/ObjectSelector.h>
#include <CommonTools/UtilAlgos/interface/SortCollectionSelector.h>
#include <DataFormats/Candidate/interface/CompositeCandidate.h>
#include <DataFormats/Candidate/interface/Candidate.h>
#include <cmath>
#include "FWCore/Framework/interface/MakerMacros.h"
#include <DataFormats/PatCandidates/interface/Jet.h>

template<typename T>
struct GreaterByCSVDiscriminator {
  typedef T first_argument_type;
  typedef T second_argument_type;
  
  bool operator()( const T & t1, const T & t2 ) const {
    return ((const pat::Jet&)t1).bDiscriminator("combinedSecondaryVertexMVABJetTags") > ((const pat::Jet&)t2).bDiscriminator("combinedSecondaryVertexMVABJetTags");
  }
};
typedef ObjectSelector< SortCollectionSelector< edm::View<reco::Candidate>, GreaterByCSVDiscriminator<reco::Candidate> > > LargestCSVDiscriminatorJetViewProducer;
DEFINE_FWK_MODULE(LargestCSVDiscriminatorJetViewProducer);

