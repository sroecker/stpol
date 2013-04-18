// -*- C++ -*-
//
// Package:    PDFweightsProducer
// Class:      PDFweightsProducer
// 
/**\class PDFweightsProducer PDFweightsProducer.cc SingleTopPolarization/PDFweightsProducer/src/PDFweightsProducer.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Mait Muntel
//         Created:  Wed Mar 13 11:20:00 EET 2013
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
#include "FWCore/MessageLogger/interface/MessageLogger.h"
#include "TMath.h"
#include <vector>
#include <map>
#include "FWCore/Framework/interface/ESHandle.h"
#include "DataFormats/HepMCCandidate/interface/PdfInfo.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include <iostream>
#include <fstream>
#include <sstream>

using namespace std;

namespace LHAPDF
{
	void initPDFSet(int nset, const std::string &filename, int member = 0);
	int numberPDF(int nset);
	void usePDFMember(int nset, int member);
	double xfx(int nset, double x, double Q, int fl);
	double getXmin(int nset, int member);
	double getXmax(int nset, int member);
	double getQ2min(int nset, int member);
	double getQ2max(int nset, int member);
	void extrapolate(bool extrapolate = true);
	int	numberPDF();
}


//
// class declaration
//

class PDFweightsProducer : public edm::EDProducer {
   public:
      explicit PDFweightsProducer(const edm::ParameterSet&);
      ~PDFweightsProducer();

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
	
	float	scalePDF;
	float	x1,x2;
	int		id1,id2;
	
	std::vector<std::string>	PDFSets;
	std::vector<std::string>	PDFnames;

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
PDFweightsProducer::PDFweightsProducer(const edm::ParameterSet& iConfig)
: PDFSets(iConfig.getParameter<std::vector<std::string>>("PDFSets"))
{
	std::map<string,int> map_name;
	
	for( unsigned int i = 0; i < PDFSets.size(); i++ ){
		if( i > 2 ) break;	// lhapdf cannot manage with more PDFs 

		// make names of PDF sets to be saved
		string name = PDFSets[i];
		size_t pos = name.find_first_not_of("ZXCVBNMASDFGHJKLQWERTYUIOPabcdefghijklmnopqrstuvwxyz1234567890");
		if (pos!=std::string::npos) name = name.substr(0,pos);
		if( map_name.count(name) == 0 ){
			map_name[name]=0;
			PDFnames.push_back(name);
		}
		else {
			map_name[name]++;
			ostringstream ostr;
			ostr << name << "xxx" << map_name[name];
			PDFnames.push_back(ostr.str());
		}
		
		produces<std::vector<double> > (string("weights"+PDFnames[i]));
		produces<double>(string("w0"+PDFnames[i]));
		produces<int>(string("n"+PDFnames[i]));
		
		// initialise the PDF set
		cout<<"PDFnames[i]="<<PDFnames[i]<<"\tPDFSets[i]="<<PDFSets[i]<<endl;
		LHAPDF::initPDFSet(i+1, PDFSets[i]);		
	}
	
}


PDFweightsProducer::~PDFweightsProducer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
PDFweightsProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	using namespace edm;
	
	// get the parton flavour, momentum fraction and energy scale
	edm::Handle<GenEventInfoProduct> genprod;
	iEvent.getByLabel("generator",genprod);

	scalePDF=	genprod->pdf()->scalePDF;
	x1		=	genprod->pdf()->x.first;
	x2		=	genprod->pdf()->x.second;
	id1		=	genprod->pdf()->id.first;
	id2		=	genprod->pdf()->id.second;
	
	
	for( unsigned int i = 0; i < PDFSets.size(); i++ ){
		if( i > 2 ) break;	// lhapdf cannot manage with more PDFs 
		
		int InitNr = i+1;
		
		// calculate the PDF weights
		std::auto_ptr < std::vector<double> > weights(new std::vector<double>());
		LHAPDF::usePDFMember(InitNr, 0);
		double	xpdf1 = LHAPDF::xfx(InitNr, x1, scalePDF, id1);
		double	xpdf2 = LHAPDF::xfx(InitNr, x2, scalePDF, id2);
		double	w0	= xpdf1 * xpdf2;
		int		nPDFSet = LHAPDF::numberPDF(InitNr);
		for (int p = 1; p <= nPDFSet; ++p)
		{
			LHAPDF::usePDFMember(InitNr, p);
			double xpdf1_new = LHAPDF::xfx(InitNr, x1, scalePDF, id1);
			double xpdf2_new = LHAPDF::xfx(InitNr, x2, scalePDF, id2);
			double pweight = xpdf1_new * xpdf2_new / w0;
			weights->push_back(pweight);
		}
		
		// save weights		
		iEvent.put(weights, string("weights"+PDFnames[i]));
		iEvent.put(std::auto_ptr<int>(new int(nPDFSet)), string("n"+PDFnames[i]));  
		iEvent.put(std::auto_ptr<double>(new double(w0)), string("w0"+PDFnames[i]));  		
		
	}
	
	
}

// ------------ method called once each job just before starting event loop  ------------
void 
PDFweightsProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PDFweightsProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void 
PDFweightsProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
PDFweightsProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
PDFweightsProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
PDFweightsProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
PDFweightsProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(PDFweightsProducer);
