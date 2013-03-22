#This script draws the b-tag weight validation plots in different jet/tag bins
#author: joosep pata joosep.pata@cern.ch
import autoLoad
import multiprocessing
import math
import re
import pickle

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")
import plotfw.methods
import plotfw.drawfw
import plotfw.params
import ROOT
import argparse
import random
import string
import os
import logging
import pdb
import numpy
from plotfw.params import Cuts
from plotfw.params import Vars

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--ofdir', type=str, default="plots_out_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4)))
    parser.add_argument('-p', '--percent', type=float, default=100.0)
    parser.add_argument('-i', '--mc_dir', type=str, default="/scratch/joosep/step2_MC_Iso_Mar14/")
    parser.add_argument('-n', '--n_cores', type=int, default=8)
    parser.add_argument('--doBWeightDistributions', action='store_true')
    parser.add_argument('--doDataMC', action='store_true')
    parser.add_argument('--doAllMC', action='store_true')
    parser.add_argument('--doEffs', action='store_true')
    parser.add_argument('--withPROOF', action='store_true')
    parser.add_argument('--do2J0T', action='store_true')
    parser.add_argument('--do2J1T', action='store_true')
    parser.add_argument('--do3J0T', action='store_true')
    parser.add_argument('--do3J1T', action='store_true')
    parser.add_argument('--do3J2T', action='store_true')
    parser.add_argument('--doLJCuts', action='store_true')
    parser.add_argument('--doCJCuts', action='store_true')
    parser.add_argument('--doJetCounts', action='store_true')
    #parser.add_argument('--allSamples', action='store_true')
    args = parser.parse_args()

    #def get_proof_output(self, name):
    #    return self.GetOutputList().FindObject(name)

    if args.withPROOF:
        p = ROOT.TProof.Open("workers=%d" % args.n_cores)
    else:
        p = None

    samples = dict()
    samples_data = dict()

    samples["TTJets_FullLept"] = plotfw.methods.MCSample("WD_TTJets_FullLept", name="TTJets_FullLept", directory=args.mc_dir)
    samples["TTJets_SemiLept"] = plotfw.methods.MCSample("WD_TTJets_SemiLept", name="TTJets_SemiLept", directory=args.mc_dir)
    samples["TTJets_inclusive"] = plotfw.methods.MCSample("WD_TTJets_MassiveBinDECAY", name="TTbar", directory=args.mc_dir)
    samples["T_t"] = plotfw.methods.MCSample("WD_T_t", name="T_t", directory=args.mc_dir)
    samples["W1Jets"] = plotfw.methods.MCSample("WD_W1Jets_exclusive", name="W1Jets", directory=args.mc_dir)
    samples["W2Jets"] = plotfw.methods.MCSample("WD_W2Jets_exclusive", name="W2Jets", directory=args.mc_dir)
    samples["W3Jets"] = plotfw.methods.MCSample("WD_W3Jets_exclusive", name="W3Jets", directory=args.mc_dir)
    samples["W4Jets"] = plotfw.methods.MCSample("WD_W4Jets_exclusive", name="W4Jets", directory=args.mc_dir)
    #samples["WJets_inclusive"] = plotfw.methods.MCSample("WD_WJets_inclusive", name="WJets", directory=args.mc_dir)

    groups = plotfw.methods.SampleGroup.fromList(samples.values())

    psMu = []
    sl = plotfw.methods.SampleList()
    sl.addGroups(groups)

    if args.doBWeightDistributions:
        comp_samples = plotfw.drawfw.ShapePlotCreator(sl)
        comp_samples.frac_entries = args.percent/100.0
        comp_samples.set_n_cores(args.n_cores)
        comp_samples.proof = p
        weightPlots = [
            plotfw.drawfw.PlotParams(Vars.b_weight["nominal"], (0, 5), doLogY=True, normalize_to="unity", ymin=0.01),
        ]
        if args.doJetCounts:
            weightPlots += [
                plotfw.drawfw.PlotParams(Vars.jet_counts_true["l"], (0, 5), bins=5, doLogY=True, normalize_to="unity"),
                plotfw.drawfw.PlotParams(Vars.jet_counts_true["b"], (0, 5), bins=5, doLogY=True, normalize_to="unity"),
                plotfw.drawfw.PlotParams(Vars.jet_counts_true["c"], (0, 5), bins=5, doLogY=True, normalize_to="unity"),
            ]
        weightPlots[0].putStats()

        if args.do2J0T:
            psMu += comp_samples.plot(Cuts.finalMu_2J0T, weightPlots, cutDescription="muon channel, final sel. (2J0T)")
            if args.doLJCuts:
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_2LJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 2 true light jets)")
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_1LJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 1 true light jet)")
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_0LJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 0 true light jets)")
            if args.doCJCuts:
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_2CJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 2 true c-jets)")
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_1CJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 1 true c-jet)")
                psMu += comp_samples.plot(Cuts.finalMu_2J0T*Cuts.jets_0CJ_true, weightPlots, cutDescription="muon channel, final sel. (2J0T, 0 true c-jets)")

        if args.do2J1T:
            psMu += comp_samples.plot(Cuts.finalMu_2J1T, weightPlots, cutDescription="muon channel, final sel. (2J1T)")

        #psMu += comp_samples.plot(Cuts.finalMu_3J0T, weightPlots, cutDescription="muon channel, final sel. (3J0T)")

        if args.do3J1T:
            psMu += comp_samples.plot(Cuts.finalMu_3J1T, weightPlots, cutDescription="muon channel, final sel. (3J1T)")

            if args.doLJCuts:
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_2LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 2 true light jets)")
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_1LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 1 true light jet)")
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_0LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 0 true light jet)")
<<<<<<< HEAD
            if args.doCJuts:
=======
            if args.doCJCuts:
>>>>>>> plots_tune
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_2CJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 2 true c-jets)")
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_1CJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 1 true c-jet)")
                psMu += comp_samples.plot(Cuts.finalMu_3J1T*Cuts.jets_0CJ_true, weightPlots, cutDescription="muon channel, final sel. (3J1T, 0 true c-jet)")

        if args.do3J0T:
            psMu += comp_samples.plot(Cuts.finalMu_3J0T, weightPlots, cutDescription="muon channel, final sel. (3J0T)")
            if args.doLJCuts:
                psMu += comp_samples.plot(Cuts.finalMu_3J0T*Cuts.jets_2LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J0T, 2 true light jets)")
                psMu += comp_samples.plot(Cuts.finalMu_3J0T*Cuts.jets_1LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J0T, 1 true light jet)")
                psMu += comp_samples.plot(Cuts.finalMu_3J0T*Cuts.jets_0LJ_true, weightPlots, cutDescription="muon channel, final sel. (3J0T, 0 true light jets)")

        #psMu += comp_samples.plot(Cuts.finalMu_2J1T, weightPlots, cutDescription="muon channel, final sel. (2J1T)")
        #psMu += comp_samples.plot(Cuts.finalMu_3J0T, weightPlots, cutDescription="muon channel, final sel. (3J0T)")
        #psMu += comp_samples.plot(Cuts.finalMu_3J1T, weightPlots, cutDescription="muon channel, final sel. (3J1T)")
        #psMu += comp_samples.plot(Cuts.finalMu_3J2T, weightPlots, cutDescription="muon channel, final sel. (3J2T)")
        if args.doAllMC:
            psMu += comp_samples.plot(Cuts.initial, weightPlots, cutDescription="all events")
    if args.doDataMC:
        samples_data["SingleMu"] = plotfw.methods.DataSample("/home/joosep/singletop/stpol/crabs/step2_Data_Iso_Mar11/*Mu*/res/*.root", 20000, name="SingleMu")
        data_group = plotfw.methods.SampleGroup("data", ROOT.kBlack)
        data_group.add(samples_data["SingleMu"])
        data_mc_comp = plotfw.drawfw.StackPlotCreator(data_group, sl)
        data_mc_comp.proof = p
        finalPlots = [
            plotfw.drawfw.PlotParams(Vars.cos_theta, (-1, 1))
        ]
        psMu += data_mc_comp.plot(Cuts.finalMu_2J1T, finalPlots, cutDescription="muon channel, final sel.")

    if len(psMu)>0:
        os.mkdir(args.ofdir)
        #pickle_file = open(args.ofdir + "/plots_mu.pickle", "w")
        #pickle.dump(psMu, pickle_file)
        #pickle_file.close()
        tfile = ROOT.TFile(args.ofdir + "/plots.root", "RECREATE")
        for p in psMu:
            p.saveToROOT(tfile)
            p.save(ofdir=args.ofdir, fmt="pdf", log=False)

    def calcSampleEffs(x):
        sample = x[1]
        def effUnc(eff, count):
            if eff>1.0 or eff<0 or count<=0:
                return -1
            else:
                return math.sqrt(eff*(1.0-eff)/count)
        eff_map_cut = dict()
        flavours = ["b", "c", "l"]
        for cutname, cut in [("2J", Cuts.mu * Cuts.Orso * Cuts.jets_2J), ("3J", Cuts.mu * Cuts.Orso * Cuts.jets_3J)]:
            eff_map_flavour = dict()
            for f in flavours:
                all = sample.getColumn(Vars.jet_counts_true[f], cut, dtype="uint32")
                tagged = sample.getColumn(Vars.jet_counts_tagged_true[f], cut, dtype="uint32")
                sum_all = numpy.sum(all)
                sum_tagged = numpy.sum(tagged)
                if sum_all>0:
                     eff = sum_tagged / float(sum_all)
                     sigma_eff = effUnc(eff, sum_tagged)
                else:
                    eff = -1
                    sigma_eff = -1
                eff_map_flavour[f] = (eff, sigma_eff)
            eff_map_cut[cutname] = eff_map_flavour
        return eff_map_flavour

    if args.doEffs:
        samples_list = samples.items()
        effs = map(calcSampleEffs, samples_list)
        result = zip(samples_list, effs)

        for ((name, sample), eff_map) in result:
            eff_2J = dict()
            eff_3J = dict()
            for (eff_s, eff) in eff_map.items():
                m = re.match("([0-9])J_([bcl])", eff_s)
                if int(m.group(1))==2:
                    eff_2J[m.group(2)] = eff
                elif int(m.group(1))==3:
                    eff_3J[m.group(2)] = eff
            print "eff_ex_%s_2J =  %s" % (name, eff_2J)
            print "eff_ex_%s_3J =  %s" % (name, eff_3J)
