#include <TFile.h>
#include <TChain.h>
#include <TEntryList.h>
#include <TROOT.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TTreePerfStats.h>
#include <TRint.h>

#include <iostream>

int main() {
    TChain *ch = new TChain("Events");
    ch->Add("/Users/joosep/Documents/stpol/WD_T_t/res/*.root");
    std::cout << "Tree has " << ch->GetEntries() << " entries." << std::endl;
    long entries = ch->GetEntries();
    int muCount = -1;

    const char* cut_str = "((((((((((int_muonCount__STPOLSEL2.obj==1) && (floats_goodSignalMuonsNTupleProducer_relIso_STPOLSEL2.obj[0]<0.12)) && (int_looseVetoMuCount__STPOLSEL2.obj==0)) && (int_looseVetoEleCount__STPOLSEL2.obj==0)) && (double_muAndMETMT__STPOLSEL2.obj > 50)) && ((floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]>130) && (floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]<220))) && ((floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[0]>40) && (floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[1]>40))) && (abs(floats_lowestBTagJetNTupleProducer_Eta_STPOLSEL2.obj[0])>2.5)) && (abs(floats_goodJetsNTupleProducer_Eta_STPOLSEL2.obj[0])<4.5 && abs(floats_goodJetsNTupleProducer_Eta_STPOLSEL2.obj[1])<4.5)) && ((int_lightJetCount__STPOLSEL2.obj==2) && (int_bJetCount__STPOLSEL2.obj==0))) && (int_trueLJetCount__STPOLSEL2.obj == 1)";
    ch->SetCacheSize(100*1024*1024);
//    ch->AddBranchToCache("*", 1);
    long n_drawn = ch->Draw(">>elist", cut_str, "entrylist");
    TEntryList* elist = (TEntryList*)gROOT->Get("elist");
    ch->SetEntryList(elist);
    ch->PrintCacheStats();
    delete ch;
    delete elist;
    return 0;
}
