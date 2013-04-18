{
   gROOT->Reset();
   TFile f("sync_step2.root");
   TTree* t = f->Get("Events"); 
   Int_t nevent = t->GetEntries();
   int trueC = -1;
   t->SetMakeClass(1); //For some reason this is required - never mind why
   t->SetBranchAddress("int_trueCJetCount__STPOLSEL2.obj", &trueC);
   for (Int_t i=0;i<nevent;i++) {
       t->GetEntry(i);
       if (trueC!=-1)
           std::cout << trueC << std::endl;
   }
}
