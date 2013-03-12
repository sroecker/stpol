/* \class CandViewNtpProducer
 * 
 * Configurable Candidate ntuple creator
 *
 * \author: Luca Lista, INFN
 *
 */
#include "FWCore/Framework/interface/MakerMacros.h"
#include "CommonTools/UtilAlgos/interface/NtpProducer.h"
#include "DataFormats/Candidate/interface/Candidate.h"

typedef NtpProducer<reco::CandidateView> CandViewNtpProducer2;

DEFINE_FWK_MODULE( CandViewNtpProducer2 );

