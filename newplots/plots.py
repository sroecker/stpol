import argparse
import ROOT
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")

from plotfw import drawfw
from plotfw.params import Cuts as cutlist
import plotfw.methods
from plotfw.params import Cut
from plotfw.params import Cut, Vars
import pdb
import samples
import os
import random
import string

logger = logging.getLogger(__name__)

"""
Copy PlotParams type objects, adding weights.
plot_params - list of PlotParams
"""
def reweighted(plot_params, do_pu=False, do_btag=True):
    out = []

    #Loop over list of PlotParams
    for pp in plot_params:
        out.append(pp)

        #Add PU weight
        if do_pu:
            plot_PUrew = drawfw.PlotParams(pp.var, pp.r,
                    bins=pp.bins, plotTitle=pp.plotTitle + " with PU(N_{true}) rew.",
                    doLogY=pp.doLogY, weights=["PUWeightNtrue_puWeightProducer"], vars_to_enable=pp.vars_to_enable, x_label=pp.x_label
            )
            out.append(plot_PUrew)

        #Add b-tag weight
        if do_btag:
            plot_bTagrew = drawfw.PlotParams(pp.var, pp.r,
                    bins=pp.bins, plotTitle=pp.plotTitle + " with bTag rew.",
                    doLogY=pp.doLogY, weights=Vars.b_weight["nominal"], vars_to_enable=pp.vars_to_enable, x_label=pp.x_label)
            out.append(plot_bTagrew)

        if do_pu and do_btag:
            plot_bTagPUrew = drawfw.PlotParams(pp.var, pp.r,
                    bins=pp.bins, plotTitle=pp.plotTitle + " with PU(N_{true}), bTag rew.",
                    doLogY=pp.doLogY, weights=["bTagWeight_bTagWeightProducerNJMT", "PUWeightNtrue_puWeightProducer"],
                    vars_to_enable=pp.vars_to_enable, x_label=pp.x_label)
            out.append(plot_bTagPUrew)
    return out

def replaceQCD(plot, histQCD, histnonQCD):
    #assert isinstance(plot, drawfw.StackPlot)
    histQCD.SetTitle("data-driven QCD")
    histnonQCD.SetTitle("data-driven non-QCD")
    plot.hist_stack.RecursiveRemove(plot.mc_group_hists["QCD"])
    plot.mc_group_hists["QCD"] = histQCD
    plot.hist_stack.Add(plot.mc_group_hists["QCD"])
    #plot.mc_group_hists["nonQCD"] = histnonQCD
    return plot

if __name__ == "__main__":
#    datasmplsMu, datasmplsEle, smpls, samples.pltcMu, pltcEle = initSamples()
    logger.info("Running plots.py")
    smpls, smplsMu, smplsAllMC, smplsWJets_incl_excl, smplsTTbar_incl_excl = samples.load()

    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--ofdir', type=str, default="plots_out_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4)))
    parser.add_argument('-n', '--n_cores', type=int, default=1)
    parser.add_argument('--doReweighted', action='store_true')
    parser.add_argument('--doLepIso', action='store_true')
    parser.add_argument('--doNJets', action='store_true')
    parser.add_argument('--doNBTags', action='store_true')
    parser.add_argument('--doMET', action='store_true')
    parser.add_argument('--doBDiscriminators', action='store_true')
    parser.add_argument('--doTopMass', action='store_true')
    parser.add_argument('--doFinalSel', action='store_true')
    parser.add_argument('--doPVCount', action='store_true')
    parser.add_argument('--doEtaLJ', action='store_true')
    parser.add_argument('--doWeights', action='store_true')
    parser.add_argument('--doWJetsControl', action='store_true')
    parser.add_argument('--doTTbarControl', action='store_true')
    #parser.add_argument('--maxLines', type=int, default=None)
    parser.add_argument('-p', '--percent', type=float, default=100.0)
    args = parser.parse_args()
    print args

    n_cores = args.n_cores
    logging.info("Using %d cores" % n_cores)
    logging.info("Running on %.2f percent of events" % args.percent)
    #samples.pltcMu.maxLines = args.maxLines
    #samples.pltcEle.maxLines = args.maxLines
    samples.pltcEle.frac_entries = args.percent/100.0
    samples.pltcMu.frac_entries = args.percent/100.0
    samples.pltcMu.set_n_cores(n_cores)
    samples.pltcEle.set_n_cores(n_cores)

    #qcdFile = ROOT.TFile("../mtwMass_fit_2J_1T_SR.root")
    #datadrivenQCD = qcdFile.Get("mtwMass__qcd")
    #datadrivenNonQCD = qcdFile.Get("mtwMass__nonqcd")

    psMu = []
    psEle = []

    if args.doLepIso:
        sigQCD = plotfw.methods.SampleList()
        sigQCD.addGroup(smpls.groups["t-channel"])
        sigQCD.addGroup(smpls.groups["QCD"])
        sigQCDshapeComp = drawfw.ShapePlotCreator(sigQCD)
        lepIsoPlots = [
            drawfw.PlotParams("_muonsWithIso_0_relIso", (0, 0.5),
                doLogY=True, plotTitle="muon delta-beta corr. rel. iso.",
                x_label="rel.iso(#mu)_{#Delta #beta)")
        ]
        psMu += sigQCDshapeComp.plot(cutlist.initial, lepIsoPlots, cutDescription="skimmed MC")
        #Plot the lepton rel. iso distributions

    if args.doNJets:
        #Plot the NJet distribution in the muon/ele channel
        jetPlots = [
            drawfw.PlotParams(
                Vars.n_jets, (1, 6),
                bins=6, plotTitle="N_{jets}", vars_to_enable=["_lightJetCount", "_bJetCount"], doLogY=True
            )
        ]

        if args.doReweighted:
            jetPlots = reweighted(jetPlots)
        psMu += samples.pltcMu.plot(cutlist.jets_OK * cutlist.mu * cutlist.MTmu, jetPlots, cutDescription="mu channel, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.jets_OK * cutlist.ele, jetPlots, cutDescription="ele channel")


    if args.doNBTags:
        #Plot the N-bTag distribution in 2J
        jetPlots2J = [drawfw.PlotParams(Vars.n_tags, (0, 3), bins=4, plotTitle="N_{b-tags}", x_label="N_{b-tags}", doLogY=True)]
        if args.doReweighted:
            jetPlots2J = reweighted(jetPlots2J)
        psMu += samples.pltcMu.plot(cutlist.jets_2J * cutlist.mu * cutlist.MTmu, jetPlots2J, cutDescription="mu channel, 2J, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.jets_2J * cutlist.ele, jetPlots2J, cutDescription="ele channel, 2J")

    if args.doMET:
        #MET/MtW distribution
        metPlotsMu = [drawfw.PlotParams(Vars.mtw_mu, (0, 150), plotTitle="M_{t}(W)")]
        metPlotsEle = [drawfw.PlotParams(Vars.met, (0, 150), plotTitle="MET")]
        if args.doReweighted:
            metPlotsMu = reweighted(metPlotsMu)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J, metPlotsMu, cutDescription="mu channel, 2J")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J, metPlotsEle, cutDescription="ele. channel, 2J")

    if args.doBDiscriminators:
        #Plot b-discriminator of highest and lowest b-tagged jet in the muon channel
        bDiscrLabel = "b-discr._{TCHP}"
        jetbDiscrPlots = [
            drawfw.PlotParams('_highestBTagJet_0_bDiscriminator', (0, 10),
                plotTitle="TCHP discriminator of the b-jet", doLogY=True, x_label=bDiscrLabel),
            drawfw.PlotParams('_lowestBTagJet_0_bDiscriminator', (0, 10),
                plotTitle="TCHP discriminator of the light jet", doLogY=True, x_label=bDiscrLabel),
        ]
        if args.doReweighted:
            jetbDiscrPlots = reweighted(jetbDiscrPlots)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J * cutlist.MTmu, jetbDiscrPlots, cutDescription="mu channel, 2J, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.ele * cutlist.jets_2J * cutlist.MTele, jetbDiscrPlots, cutDescription="ele channel, 2J, MET>45 GeV")

    if args.doTopMass:
        #top mass plot
        topMassPlots = [
            drawfw.PlotParams('_recoTop_0_Mass', (100, 500), plotTitle="M_{bl#nu}", x_label="M_{bl#nu}", doLogY=True),
        ]
        if args.doReweighted:
            topMassPlots = reweighted(topMassPlots)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J1T * cutlist.etaLJ * cutlist.MTmu,
                topMassPlots, cutDescription="mu channel, 2J1T, |#eta|_{lj}>2.5, M_{t}(W)>50 GeV")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T, MET>45 GeV")

    if args.doEtaLJ:
        #Light jet plots
        etaljLabel = "#eta_{lj}"
        lightJetPlots = [
            drawfw.PlotParams('_lowestBTagJet_0_Eta', (-5, 5),
                plotTitle="#eta of the light jet", x_label=etaljLabel),
            drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5),
                plotTitle="|#eta| of the light jet", vars_to_enable=["_lowestBTagJet_0_Eta"], x_label=etaljLabel),
            drawfw.PlotParams('_lowestBTagJet_0_rms', (0, 0.15),
                plotTitle="rms of the light jet constituents", doLogY=True, x_label=etaljLabel)
        ]
        if doReweighted:
            lightJetPlots = reweighted(lightJetPlots)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J1T * cutlist.MTmu, lightJetPlots, cutDescription="mu channel, 2J1T, M_{t}(W)>50 GeV")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T")

    if args.doFinalSel:
        #Plot cosTheta* etc in the final selection
        finalSelPlots = [
            drawfw.PlotParams(Vars.cos_theta, (-1, 1),
                plotTitle="cos #theta_{lj}", x_label="cos #theta_{lj}"
            )
        ]

        #mtwDataDrivenPlot = [
        #    drawfw.PlotParams('_muAndMETMT', (0, 200), bins=20,
        #        plotTitle="M_{t}(W)", x_label="M_{t}(W) [GeV]"
        #    )
        #]
        if args.doReweighted:
            finalSelPlots = reweighted(finalSelPlots)
        for p in finalSelPlots:
            p.doChi2Test("mc", "data", chi2options={"weight_type":"WW"})
        psMu += samples.pltcMu.plot(cutlist.finalMu_2J1T, reversed(finalSelPlots), cutDescription="mu channel, 2J1T, final selection")

        #cutMTWDataDriven = Cut("mtwDataDriven", "_muonCount == 1 && _topCount == 1 && cosThetaLightJet_cosTheta==cosThetaLightJet_cosTheta && _goodJets_0_Pt>40 && _goodJets_1_Pt>40 && abs(_lowestBTagJet_0_Eta)>2.5 && _bJetCount == 1 && _lightJetCount == 1 && abs(_recoTop_0_Mass - 172) < 40 && _goodSignalMuons_0_relIso<0.12 && _lowestBTagJet_0_rms<0.025")
        #psMu += map(lambda x: replaceQCD(x, datadrivenQCD, datadrivenNonQCD), samples.pltcMu.plot(cutMTWDataDriven, mtwDataDrivenPlot, cutDescription=""))
        #psEle += pltcEle.plot(cutlist.finalEle, finalSelPlots, cutDescription="ele channel, 2J1T, final selection")


    if args.doPVCount:
        sigDataMu = plotfw.methods.SampleList()
        sigDataMu.addGroup(smpls.groups["t-channel"])
        sigDataMu.addGroup(smplsMu)
        sigDataMuShapeComp = drawfw.ShapePlotCreator(sigDataMu, n_cores=n_cores)
        NvtxPlots = [
                drawfw.PlotParams("_offlinePVCount", (0, 60), plotTitle="reconstructed N_{vtx.} before PU rew."),
        ]
        if args.doReweighted:
            NvtxPlots.append(drawfw.PlotParams("_offlinePVCount", (0, 60), plotTitle="reconstructed N_{vtx.} after PU rew.(N_{true})",
                    weights=["PUWeightNtrue_puWeightProducer"]))

        for p in NvtxPlots:
            p.doChi2Test("t-channel", "mu", chi2options={"weight_type":"WW"})

        psMu += sigDataMuShapeComp.plot(cutlist.finalMu, NvtxPlots, cutDescription="muon channel, final sel.")
        #allMCDataMu = plotfw.methods.SampleList()
        #allMCDataMu.addGroup(smplsAllMC)
        #allMCDataMu.addGroup(smplsMu)
        #allMCDataMuShapeComp = drawfw.ShapePlotCreator(allMCDataMu, n_cores=n_cores)
        #psMu += allMCDataMuShapeComp.plot(cutlist.initial, NvtxPlots, cutDescription="skimmed MC")
        #psMu += allMCDataMuShapeComp.plot(cutlist.finalMu, NvtxPlots, cutDescription="muon channel, final sel.")

    if args.doWeights:

        sigMainBKG = plotfw.methods.SampleList()
        sigMainBKG.addGroup(smpls.groups["t-channel"])
        sigMainBKG.addGroup(smpls.groups["TTbar"])
        sigMainBKG.addGroup(smpls.groups["WJets"])
        sigMainBKGComp = drawfw.ShapePlotCreator(sigMainBKG, n_cores=n_cores)
        weightPlots = [
            drawfw.PlotParams("bTagWeight_bTagWeightProducerNJMT", (0.8, 1.2), doLogY=False, plotTitle="b-tag weight (nominal)", normalize_to="unity"),
            drawfw.PlotParams("bTagWeight_bTagWeightProducerNJMT", (0.8, 1.2), doLogY=False, plotTitle="b-tag weight (nominal)", normalize_to="lumi"),
    #        drawfw.PlotParams("PUWeightNtrue_puWeightProducer", (0, 5), doLogY=False, plotTitle="PU weight (N_{true})", normalize_to="unity"),
    #        drawfw.PlotParams("PUWeightN0_puWeightProducer", (0, 5), doLogY=True, plotTitle="PU weight (N_{0})")
        ]
        for p in weightPlots:
            p.putStats()
        #psMu += sigMainBKGComp.plot(cutlist.initial, weightPlots, cutDescription="skimmed MC")
        psMu += sigMainBKGComp.plot(cutlist.finalMu, weightPlots, cutDescription="muon channel, final sel.")

    if args.doWJetsControl:
        wjetsComp = drawfw.ShapePlotCreator(smplsWJets_incl_excl, n_cores=n_cores)
        wjetsPlots = [
            drawfw.PlotParams("_lowestBTagJet_0_Eta", (-5, 5), doLogY=False, plotTitle="#eta_{lj}", normalize_to="lumi"),
        ]
        for p in wjetsPlots:
            p.doChi2Test("WJets_inclusive", "WJets_exclusive", chi2options={"weight_type":"WW"})
        psMu += wjetsComp.plot(cutlist.initial * cutlist.jets_2J0T * cutlist.mu * cutlist.MTmu, wjetsPlots, cutDescription="2J0T, muon channel, M_{t}(W)>50 GeV")

    if args.doTTbarControl:
        ttbarComp = drawfw.ShapePlotCreator(smplsTTbar_incl_excl, n_cores=n_cores)
        ttbarPlots = [
            drawfw.PlotParams("_lowestBTagJet_0_Eta", (-5, 5), doLogY=False, plotTitle="#eta_{lj}", normalize_to="lumi"),
            drawfw.PlotParams("_highestBTagJet_0_Eta", (-5, 5), doLogY=False, plotTitle="#eta_{b-jet}", normalize_to="lumi"),
            drawfw.PlotParams("bTagWeight_bTagWeightProducerNJMT", (0.1, 2), plotTitle="b-weight (nominal)", normalize_to="lumi"),
        ]
        for p in ttbarPlots:
            p.doChi2Test("TTbar_inclusive", "TTbar_exclusive", chi2options={"weight_type":"WW"})
        psMu += ttbarComp.plot(cutlist.initial * cutlist.jets_3J1T * cutlist.mu * cutlist.MTmu, ttbarPlots, cutDescription="3J1T, muon channel, M_{t}(W)>50 GeV")

    if args.doBWeightControl:
        bWeightPlots = [
            drawfw.PlotParams("_bJetCount", (0, 3), bins=3, plotTitle="N_{b-tags}", normalize_to="lumi"),
            drawfw.PlotParams("_lowestBTagJet_0_Eta", (-5, 5), plotTitle="#eta_{lj}", normalize_to="lumi"),
            drawfw.PlotParams("_highestBTagJet_0_Eta", (-5, 5), plotTitle="#eta_{b-jet}", normalize_to="lumi"),
            drawfw.PlotParams("bTagWeight_bTagWeightProducerNJMT", (0.1, 2), plotTitle="b-weight (nominal)", normalize_to="lumi"),
        ]
        if args.doReweighted:
            bWeightPlots = reweighted(bWeightPlots)
        for p in bWeightPlots:
            p.doChi2Test("mc", "data", chi2options={"weight_type": "WW"})
        psMu += samples.pltcMu.plot(cutlist.initial*cutlist.jets_3J2T*cutlist.mu*cutlist.MTmu, bWeightPlots, cutDescription="3J2T, muon channel, M_{t}(W)>50 GeV")
        psMu += samples.pltcMu.plot(cutlist.finalMu, bWeightPlots, cutDescription="muon channel, final selection")

    ps = psMu + psEle
    i = 1
    os.mkdir(args.ofdir)
    for p in ps:
        p.save(ofdir=args.ofdir, fmt="pdf", log=True)
        i += 1
