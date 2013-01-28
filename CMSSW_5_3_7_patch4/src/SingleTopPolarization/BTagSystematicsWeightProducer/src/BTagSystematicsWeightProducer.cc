// -*- C++ -*-
//
// Package:    BTagSystematicsWeightProducer
// Class:      BTagSystematicsWeightProducer
// 
/**\class BTagSystematicsWeightProducer BTagSystematicsWeightProducer.cc SingleTopPolarization/BTagSystematicsWeightProducer/src/BTagSystematicsWeightProducer.cc

 Description: Produces the b-tag reweight from the b-tagging efficiency and the scale factor, along with the up/down variation of this weight.

 Implementation:
     
*/
//
// Original Author:  Joosep Pata
//         Created:  Fri Dec 21 16:47:11 EET 2012
// $Id$
//
//


// system include files
#include <memory>
#include <algorithm>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include <TFormula.h>
#include <TMath.h>

#include <string.h>


//
// class declaration
//

typedef std::vector<std::vector<unsigned int>> Combinations;

class BTagSystematicsWeightProducer : public edm::EDProducer {
   public:
      enum Flavour {
          b,c,l
      };
      enum BTagAlgo {
          CSVM
      };
      explicit BTagSystematicsWeightProducer(const edm::ParameterSet&);
      ~BTagSystematicsWeightProducer();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

   private:
      virtual void beginJob() ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;
      
      virtual void beginRun(edm::Run&, edm::EventSetup const&);
      virtual void endRun(edm::Run&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);


      void combinations(const unsigned int n, const unsigned int k, Combinations& combs);
      
      const std::unique_ptr<std::map<BTagSystematicsWeightProducer::Flavour, double>> effs; 
      const edm::InputTag jetSrc;
      const unsigned int nJets, nTags; 
      Combinations combs;
      double scaleFactor(BTagSystematicsWeightProducer::Flavour flavour, BTagSystematicsWeightProducer::BTagAlgo algo, double pt, double eta, double& sfUp, double& sfDown);
      double piecewise(double x, const std::vector<double>& bin_low, const std::vector<double>& bin_val);
      
      static const std::vector<double> SFb_ptBins; 
      static const std::vector<double> SFb_CSVM_Err;
      const BTagSystematicsWeightProducer::BTagAlgo bTagAlgo;
      // ----------member data ---------------------------
};


const std::vector<double> BTagSystematicsWeightProducer::SFb_ptBins ({
                20,
                30,
                40,
                50,
                60,
                70,
                80,
                100,
                120,
                160,
                210,
                260,
                320,
                400,
                500,
                600,
                800
});

const std::vector<double> BTagSystematicsWeightProducer::SFb_CSVM_Err ({
                0.0554504,
                0.0209663,
                0.0207019,
                0.0230073,
                0.0208719,
                0.0200453,
                0.0264232,
                0.0240102,
                0.0229375,
                0.0184615,
                0.0216242,
                0.0248119,
                0.0465748,
                0.0474666,
                0.0718173,
                0.0717567
});

//bin_low must be sorted ascending, contains the lower values of bins.
//The final bin_low contains the upper value of the last bin.
//bin_val must contain bin_low.size()-1 values.
double BTagSystematicsWeightProducer::piecewise(double x, const std::vector<double>& bin_low, const std::vector<double>& bin_val)
{
    assert(bin_low.size() == bin_val.size()+1);
    assert(bin_low.size() > 0);
    if (x<bin_low[0]) {
        LogDebug("piecewise") << "underflow: " << x << "<" << bin_low[0];
        return TMath::QuietNaN();
    }
    for(unsigned int i=1;i<bin_low.size();i++) {
        if(bin_low[i] > x)
            return bin_val[i-1];
    }
    if(x == bin_low[bin_low.size()-1])
        return bin_val[bin_val.size()-1];

    LogDebug("piecewise") << "overflow: " << x << ">" << bin_low[bin_low.size()-1];
    return TMath::QuietNaN();
}

double BTagSystematicsWeightProducer::scaleFactor(BTagSystematicsWeightProducer::Flavour flavour, BTagSystematicsWeightProducer::BTagAlgo algo, double pt, double eta_, double& sfUp, double& sfDown) {
    double sf = 0.0; 
    double eta = fabs(eta_);
    bool ptOverFlow = false; 
    bool ptUnderFlow = false; 
    bool etaOverFlow = false; 

    if (pt>800.0){
        pt=800.0;
        ptOverFlow = true;
    }
    if (pt<20.0) {
        pt=20.0;
        ptUnderFlow = true;
    }
    if (fabs(eta)>2.4) {
        etaOverFlow = true;
    }

    if(etaOverFlow) {
      edm::LogInfo("scaleFactor") << "eta overflow: " << eta << ">" << "2.4, setting scale factors to 1";
      sf = 1.0;
      sfUp = 1.0;
      sfDown = 1.0;
      return sf;
    }

    auto SFerr = [&sf, &sfUp, &sfDown] (double sfErr) {
        sfUp = sf + sfErr;
        sfDown = sf - sfErr;
    };

    auto sfB_CSVM = [&pt] () {
        double x = pt;
        return 0.726981*((1.+(0.253238*x))/(1.+(0.188389*x)));
    };

    auto sfL_CSVM = [&eta, &pt, &sfUp, &sfDown] () {
        double x = pt;

        //Data period ABCD
        if(eta >= 0.0 && eta < 0.8) {
            sfDown = ((0.972746+(0.00104424*x))+(-2.36081e-06*(x*x)))+(1.53438e-09*(x*(x*x)));
            sfUp = ((1.15201+(0.00292575*x))+(-7.41497e-06*(x*x)))+(5.0512e-09*(x*(x*x)));
            return ((1.06238+(0.00198635*x))+(-4.89082e-06*(x*x)))+(3.29312e-09*(x*(x*x)));
        }
        else if(eta >= 0.8 && eta < 1.6) {
            sfDown = ((0.9836+(0.000649761*x))+(-1.59773e-06*(x*x)))+(1.14324e-09*(x*(x*x)));
            sfUp = ((1.17735+(0.00156533*x))+(-4.32257e-06*(x*x)))+(3.18197e-09*(x*(x*x)));
            return ((1.08048+(0.00110831*x))+(-2.96189e-06*(x*x)))+(2.16266e-09*(x*(x*x)));
        }
        else if(eta >= 1.6 && eta < 2.4) {
            sfDown = ((1.00616+(0.000358884*x))+(-1.23768e-06*(x*x)))+(6.86678e-10*(x*(x*x)));
            sfUp = ((1.17671+(0.0010147*x))+(-3.66269e-06*(x*x)))+(2.88425e-09*(x*(x*x)));
            return ((1.09145+(0.000687171*x))+(-2.45054e-06*(x*x)))+(1.7844e-09*(x*(x*x)));   
        }
        else {
          return TMath::QuietNaN();
        }
    };
    
    if( flavour == BTagSystematicsWeightProducer::b ) {
        if( algo == BTagSystematicsWeightProducer::CSVM ) {
            sf = sfB_CSVM();
            //double sfErr = 0;
            double sfErr = piecewise(pt, SFb_ptBins, SFb_CSVM_Err);
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr; 
            SFerr(sfErr); 
        } else {
            throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
        }
    }
    else if( flavour==BTagSystematicsWeightProducer::c ) {
        
        //for c use the b SF but increase unc. by a factor of 2
        if(algo == BTagSystematicsWeightProducer::CSVM) {
            sf = sfB_CSVM();
            double sfErr = piecewise(pt, BTagSystematicsWeightProducer::SFb_ptBins, BTagSystematicsWeightProducer::SFb_CSVM_Err);
            sfErr = 2*sfErr;  
            if(ptOverFlow || ptUnderFlow)
                sfErr = 2*sfErr; 
            SFerr(sfErr); 
        } else {
            throw cms::Exception("scaleFactor") << "algo " << algo << " not implemented";
        }
    }
    else if( flavour==BTagSystematicsWeightProducer::l) {
        sf = sfL_CSVM();
    }
    else {
        throw cms::Exception("scaleFactor") << "Unrecognized jet flavour for scaleFactor():" << flavour;
    }
    return sf;
}

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
BTagSystematicsWeightProducer::BTagSystematicsWeightProducer(const edm::ParameterSet& iConfig)
: effs(new std::map<BTagSystematicsWeightProducer::Flavour, double>())
, jetSrc(iConfig.getParameter<edm::InputTag>("src"))
, nJets(iConfig.getParameter<unsigned int>("nJets"))
, nTags(iConfig.getParameter<unsigned int>("nTags"))
, bTagAlgo(BTagSystematicsWeightProducer::CSVM)
{
   
   //The efficiencies are the probabilities of a jet of given flavour to be b-tagged. In general, these are sample-dependent.
   (*effs)[BTagSystematicsWeightProducer::b] = iConfig.getParameter<double>("effB"); 
   (*effs)[BTagSystematicsWeightProducer::c] = iConfig.getParameter<double>("effC"); 
   (*effs)[BTagSystematicsWeightProducer::l] = iConfig.getParameter<double>("effL"); 

   //Precalculate the tagging combinations 
   combinations(nJets, nTags, combs);
 
   produces<double>("bTagWeight");
   produces<double>("bTagWeightSystBCUp");
   produces<double>("bTagWeightSystBCDown");
   produces<double>("bTagWeightSystLUp");
   produces<double>("bTagWeightSystLDown");
}

/*
Produces the vector of k-length combinations of integers from the set of integers [0,n-1].
For example, combinations(3, 2, out) produces a vector of vectors with the following elements
(
(0,1)
(0,2)
(1,2)
)
*/
void BTagSystematicsWeightProducer::combinations(const unsigned int n, const unsigned int k, Combinations& combs) {
    std::vector<bool> v(n);
    std::fill(v.begin()+v.size()-k, v.end(), true);
    do {
        std::vector<unsigned int> comb;
        for(unsigned int i=0;i<v.size();i++) {
            if(v[i])
                comb.push_back(i);
        }
        combs.push_back(comb);
    }
    while(std::next_permutation(v.begin(), v.end()));
    std::reverse(combs.begin(), combs.end()); 
}


BTagSystematicsWeightProducer::~BTagSystematicsWeightProducer()
{
}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
BTagSystematicsWeightProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   Handle<View<reco::Candidate> > jets;
   iEvent.getByLabel(jetSrc, jets);

   LogDebug("produce") << "This event has " << jets->size() << " jets";
   
   double P_mc = 0.0; 
   double P_data = 0.0;
   double P_data_bcUp = 0.0;
   double P_data_bcDown = 0.0;
   double P_data_lUp = 0.0;
   double P_data_lDown = 0.0;

   for(std::vector<unsigned int>& comb : combs) {

       unsigned int jetIdx = 0; 
       double p_mc = 1.0; 
       double p_data = 1.0;
 
       double p_data_bcUp = 1.0; 
       double p_data_bcDown = 1.0; 
       double p_data_lUp = 1.0; 
       double p_data_lDown = 1.0;
 
       for (const auto& jet_ : *jets) {
           pat::Jet& jet = (pat::Jet&)jet_;

           bool inComb = std::find(comb.begin(), comb.end(), jetIdx) != comb.end();
           //bool inComb = false; 
           
           auto prob = [&, &p_mc, &p_data, inComb, jet, this] (BTagSystematicsWeightProducer::Flavour flavour) {
               LogDebug("produce") << "prob(): flavour=" << flavour;
               //assert(type == "b" || type == "c" || type == "l");

               //Returns x if _inComb==true, (1-x) otherwise
               auto eff = [] (double x, bool _inComb) -> double {
                   return _inComb ? x : 1.0 - x;
               };

               //The probability associated with a jet is eff if the jet is in the combination of b-tagged jets, (1-eff) otherwise
               double e = eff( ((*effs)[flavour]), inComb);
               
               //per-event jet probabilities multiply
               p_mc = p_mc * e;

               //Calculate the pt, eta and flavour dependent scale factors, including the flavour-dependent variations.
               double sfUp, sfDown;
               double sf = scaleFactor(flavour, BTagSystematicsWeightProducer::bTagAlgo, jet.pt(), jet.eta(), sfUp, sfDown);
               LogDebug("produce") << "e=" << e << " sf=" << sf << " sfUp=" << sfUp << " sfDown=" << sfDown;
               p_data = p_data * e * sf;
               LogDebug("produce") << "p_mc=" << p_mc << " p_data=" << p_data;
               if( flavour == BTagSystematicsWeightProducer::b || flavour == BTagSystematicsWeightProducer::c ) {
                   p_data_lUp = p_data_lUp * e * sf;
                   p_data_lDown = p_data_lDown * e * sf;
                   p_data_bcUp = p_data_bcUp * e * sfUp;
                   p_data_bcDown = p_data_bcDown * e * sfDown;
                   LogDebug("produce") << "p_data_bcUp=" << p_data_bcUp << " p_data_bcDown=" << p_data_bcDown;
               }
               else if(flavour == BTagSystematicsWeightProducer::l) {
                   p_data_lUp = p_data_lUp * e * sfUp;
                   p_data_lDown = p_data_lDown * e * sfDown;
                   p_data_bcUp = p_data_bcUp * e * sf;
                   p_data_bcDown = p_data_bcDown * e * sf;
                   LogDebug("produce") << "p_data_lUp=" << p_data_lUp << " p_data_lDown=" << p_data_lDown;
               }
           };
 
           if(abs(jet.partonFlavour()) == 5) { //b-jet
               prob(BTagSystematicsWeightProducer::b); //multiply the probability corresponding to the b-jet 
           }
           else if(abs(jet.partonFlavour())==4) { //c-jet
               prob(BTagSystematicsWeightProducer::c); 
           }
           else if(abs(jet.partonFlavour())==21 || abs(jet.partonFlavour())<=3) { //light jet
               prob(BTagSystematicsWeightProducer::l); 
           }

           jetIdx++;
       }
       
       LogDebug("produce") << "combination probs p_mc=" << p_mc << " p_data=" << p_data  << " p_data_bcUp=" << p_data_bcUp  << " p_data_bcDown=" << p_data_bcDown  << " p_data_lUp=" << p_data_lUp  << " p_data_lDown=" << p_data_lDown;
       //Probabilities of different combinations add
       P_mc += p_mc;
       P_data += p_data;


       P_data_bcUp += p_data_bcUp;
       P_data_bcDown += p_data_bcDown;
       P_data_lUp += p_data_lUp;
       P_data_lDown += p_data_lDown;

   }

   LogDebug("produce") << "event prob P_mc=" << P_mc << " P_data=" << P_data << " P_data_bcUp=" << P_data_bcUp << " P_data_bcDown=" << P_data_bcDown << " P_data_lUp=" << P_data_lUp << " P_data_lDown=" << P_data_lDown;

   double w = P_data/P_mc;
   double w_bcUp = P_data_bcUp/P_mc;
   double w_bcDown = P_data_bcDown/P_mc;
   double w_lUp = P_data_lUp/P_mc;
   double w_lDown = P_data_lDown/P_mc;
   LogDebug("produce") << "event weights w=" << w << " w_bcUp=" << w_bcUp << " w_bcDown=" << w_bcDown << " w_lUp=" << w_lUp << " w_lDown=" << w_lDown;

   iEvent.put(std::auto_ptr<double>(new double(w)), "bTagWeight");
   iEvent.put(std::auto_ptr<double>(new double(w_bcUp)), "bTagWeightSystBCUp");
   iEvent.put(std::auto_ptr<double>(new double(w_bcDown)), "bTagWeightSystBCDown");
   iEvent.put(std::auto_ptr<double>(new double(w_lUp)), "bTagWeightSystLUp");
   iEvent.put(std::auto_ptr<double>(new double(w_lDown)), "bTagWeightSystLDown");
 
}

// ------------ method called once each job just before starting event loop  ------------
void 
BTagSystematicsWeightProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
BTagSystematicsWeightProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
BTagSystematicsWeightProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
BTagSystematicsWeightProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
BTagSystematicsWeightProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
BTagSystematicsWeightProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
BTagSystematicsWeightProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(BTagSystematicsWeightProducer);
