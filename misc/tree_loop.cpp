#include <TFile.h>
#include <TChain.h>
#include <TEntryList.h>
#include <TROOT.h>
#include <TCanvas.h>
#include <TH1F.h>
#include <TTreePerfStats.h>
#include <TTreeCache.h>
#include <TRint.h>
#include <TStopwatch.h>

#include <iostream>

int main() {
    TTree* ch = 0;
    bool useChain = true;
    TTreePerfStats* perf = 0;
    TStopwatch *sw = new TStopwatch();
    if(!useChain) {
      TFile *f = new TFile("/testhome/jooseptest/T_t_merged.root");
      ch = (TTree*)f->Get("Events"); 
//      perf = new TTreePerfStats("ioperf", ch);
    }
    else {
      ch = new TChain("Events");
      ((TChain*)ch)->Add("/testhome/jooseptest/step2_MC_Iso_Mar14/WD_T_t/res/*.root");
    } 
    sw->Start();
    std::cout << "Tree has " << ch->GetEntries() << " entries." << std::endl;
    long entries = ch->GetEntries();

    const char* cut_str = "((((((((((int_muonCount__STPOLSEL2.obj==1) && (floats_goodSignalMuonsNTupleProducer_relIso_STPOLSEL2.obj[0]<0.12)) && (int_looseVetoMuCount__STPOLSEL2.obj==0)) && (int_looseVetoEleCount__STPOLSEL2.obj==0)) && (double_muAndMETMT__STPOLSEL2.obj > 50)) && ((floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]>130) && (floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]<220))) && ((floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[0]>40) && (floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[1]>40))) && (abs(floats_lowestBTagJetNTupleProducer_Eta_STPOLSEL2.obj[0])>2.5)) && (abs(floats_goodJetsNTupleProducer_Eta_STPOLSEL2.obj[0])<4.5 && abs(floats_goodJetsNTupleProducer_Eta_STPOLSEL2.obj[1])<4.5)) && ((int_lightJetCount__STPOLSEL2.obj==2) && (int_bJetCount__STPOLSEL2.obj==0))) && (int_trueLJetCount__STPOLSEL2.obj == 1)";
    ch->SetCacheSize(100*1024*1024);
    //ch->AddBranchToCache("*", 1);
    ch->Draw(">>elist", cut_str, "entrylist", 100);
    ch->StopCacheLearningPhase();
    long n_drawn = ch->Draw(">>elist", cut_str, "entrylist");
    ch->PrintCacheStats();
    TEntryList* elist = (TEntryList*)gROOT->Get("elist");
    std::cout << "events remaining after cut: " << n_drawn << std::endl;
    
    //ch->SetEntryList(elist);
    //ch->DropBranchFromCache("*", 1);
    //long n_drawn_hist = ch->Draw("floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0] >> h", "", "goff");
    //ch->PrintCacheStats();
    sw->Stop(); 
    std::cout << "event/s cpu = " << entries / sw->CpuTime() << " event/s real = " << entries/sw->RealTime() << std::endl;
    if(!useChain) {
      //perf->Finish();// << uncomment to segfault
      //perf->Paint();
      //perf->Print();
    }

    delete ch;
    delete elist;
    return 0;
}
