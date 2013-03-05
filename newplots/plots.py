import ROOT
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(message)s")

from plotfw import drawfw
from plotfw.params import Cuts as cutlist
import plotfw.methods
from plotfw.params import Cut
import pdb
import samples
import os
import random
import string

logger = logging.getLogger(__name__)
def reweighted(plot_params):
    out = []
    for pp in plot_params:
        out.append(pp)
        plot_PUrew = drawfw.PlotParams(pp.var, pp.r,
                bins=pp.bins, plotTitle=pp.plotTitle + " with PU(N_{true}) rew.",
                doLogY=pp.doLogY, weights=["PUWeightNtrue_puWeightProducer"], vars_to_enable=pp.vars_to_enable, x_label=pp.x_label
        )
        out.append(plot_PUrew)
        #plot_bTagrew = drawfw.PlotParams(pp.var, pp.r,
        #        bins=pp.bins, plotTitle=pp.plotTitle + " with bTag rew.",
        #        doLogY=pp.doLogY, weights=["bTagWeight_bTagWeightProducer"], vars_to_enable=pp.vars_to_enable, x_label=pp.x_label)
        #out.append(plot_bTagrew)
        #plot_bTagPUrew = drawfw.PlotParams(pp.var, pp.r,
        #        bins=pp.bins, plotTitle=pp.plotTitle + " with PU(N_{true}), bTag rew.",
        #        doLogY=pp.doLogY, weights=["bTagWeight_bTagWeightProducer", "PUWeightNtrue_puWeightProducer"],
        #        vars_to_enable=pp.vars_to_enable, x_label=pp.x_label)
        #out.append(plot_bTagPUrew)
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
    smpls, smplsMu = samples.load()
    samples.pltcMu.frac_entries = 1.0
    samples.pltcMu.set_n_cores(1)
    samples.pltcEle.set_n_cores(1)

    #qcdFile = ROOT.TFile("../mtwMass_fit_2J_1T_SR.root")
    #datadrivenQCD = qcdFile.Get("mtwMass__qcd")
    #datadrivenNonQCD = qcdFile.Get("mtwMass__nonqcd")

    doReweighted = True
    doLepIso = False
    doNJets = False
    doNBTags = False
    doMET = False
    doBDiscriminators = False
    doTopMass = False
    doFinalSel = True
    doPVCount = True
    doEtaLJ = False
    doWeights = False

    psMu = []
    psEle = []
    if doLepIso:
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

    if doNJets:
        #Plot the NJet distribution in the muon/ele channel
        jetPlots = [drawfw.PlotParams('_lightJetCount + _bJetCount', (1, 6),
            bins=6, plotTitle="N_{jets}", doLogY=False, vars_to_enable=["_lightJetCount", "_bJetCount"], x_label="N_{jets}")
        ]

        if doReweighted:
            jetPlots = reweighted(jetPlots)
        psMu += samples.pltcMu.plot(cutlist.jets_OK * cutlist.mu * cutlist.MTmu, jetPlots, cutDescription="mu channel, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.jets_OK * cutlist.ele, jetPlots, cutDescription="ele channel")


    if doNBTags:
        #Plot the N-bTag distribution in 2J
        jetPlots2J = [drawfw.PlotParams('_bJetCount', (0, 3), bins=4, plotTitle="N_{b-tags}", doLogY=False, x_label="N_{b-tags}")]
        if doReweighted:
            jetPlots2J = reweighted(jetPlots2J)
        psMu += samples.pltcMu.plot(cutlist.jets_2J * cutlist.mu * cutlist.MTmu, jetPlots2J, cutDescription="mu channel, 2J, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.jets_2J * cutlist.ele, jetPlots2J, cutDescription="ele channel, 2J")

    if doMET:
        #MET/MtW distribution
        metPlotsMu = [drawfw.PlotParams('_muAndMETMT', (0, 150), plotTitle="M_{t}(W)", x_label="M_{t}(W) [GeV]")]
        metPlotsEle = [drawfw.PlotParams('_patMETs_0_Pt', (0, 150), plotTitle="MET", x_label="MET [GeV]")]
        if doReweighted:
            metPlotsMu = reweighted(metPlotsMu)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J, metPlotsMu, cutDescription="mu channel, 2J")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J, metPlotsEle, cutDescription="ele. channel, 2J")

    if doBDiscriminators:
        #Plot b-discriminator of highest and lowest b-tagged jet in the muon channel
        bDiscrLabel = "b-discr._{TCHP}"
        jetbDiscrPlots = [
            drawfw.PlotParams('_highestBTagJet_0_bDiscriminator', (0, 10),
                plotTitle="TCHP discriminator of the b-jet", doLogY=True, x_label=bDiscrLabel),
            drawfw.PlotParams('_lowestBTagJet_0_bDiscriminator', (0, 10),
                plotTitle="TCHP discriminator of the light jet", doLogY=True, x_label=bDiscrLabel),
        ]
        if doReweighted:
            jetbDiscrPlots = reweighted(jetbDiscrPlots)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J * cutlist.MTmu, jetbDiscrPlots, cutDescription="mu channel, 2J, M_{t}(W)>50 GeV")
        #psEle += samples.pltcMu.plot(cutlist.ele * cutlist.jets_2J * cutlist.MTele, jetbDiscrPlots, cutDescription="ele channel, 2J, MET>45 GeV")

    if doTopMass:
        #top mass plot
        topMassPlots = [
            drawfw.PlotParams('_recoTop_0_Mass', (100, 500), plotTitle="M_{bl#nu}", x_label="M_{bl#nu}"),
        ]
        if doReweighted:
            topMassPlots = reweighted(topMassPlots)
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J1T * cutlist.etaLJ * cutlist.MTmu,
                topMassPlots, cutDescription="mu channel, 2J1T, |#eta|_{lj}>2.5, M_{t}(W)>50 GeV")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T, MET>45 GeV")

    if doEtaLJ:
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
        psMu += samples.pltcMu.plot(cutlist.mu * cutlist.jets_2J1T, lightJetPlots, cutDescription="mu channel, 2J1T")
        #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T")

    if doFinalSel:
        #Plot cosTheta* etc in the final selection
        finalSelPlots = [
            drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1),
                plotTitle="cos #theta_{lj}", x_label="cos #theta_{lj}"
            )
        ]

        mtwDataDrivenPlot = [
            drawfw.PlotParams('_muAndMETMT', (0, 200), bins=20,
                plotTitle="M_{t}(W)", x_label="M_{t}(W) [GeV]"
            )
        ]
        if doReweighted:
            finalSelPlots = reweighted(finalSelPlots)
        for p in finalSelPlots:
            p.doChi2Test("mc", "data", chi2options={"weight_type":"WW"})
        psMu += samples.pltcMu.plot(cutlist.finalMu, finalSelPlots, cutDescription="mu channel, 2J1T, final selection")

        #cutMTWDataDriven = Cut("mtwDataDriven", "_muonCount == 1 && _topCount == 1 && cosThetaLightJet_cosTheta==cosThetaLightJet_cosTheta && _goodJets_0_Pt>40 && _goodJets_1_Pt>40 && abs(_lowestBTagJet_0_Eta)>2.5 && _bJetCount == 1 && _lightJetCount == 1 && abs(_recoTop_0_Mass - 172) < 40 && _goodSignalMuons_0_relIso<0.12 && _lowestBTagJet_0_rms<0.025")
        #psMu += map(lambda x: replaceQCD(x, datadrivenQCD, datadrivenNonQCD), samples.pltcMu.plot(cutMTWDataDriven, mtwDataDrivenPlot, cutDescription=""))
        #psEle += pltcEle.plot(cutlist.finalEle, finalSelPlots, cutDescription="ele channel, 2J1T, final selection")


    if doPVCount:
        sigDataMu = plotfw.methods.SampleList()
        sigDataMu.addGroup(smpls.groups["t-channel"])
        sigDataMu.addGroup(smplsMu)
        sigDataMuShapeComp = drawfw.ShapePlotCreator(sigDataMu, n_cores=1)
        NvtxPlots = [
                drawfw.PlotParams("_offlinePVCount", (0, 60), plotTitle="reconstructed N_{vtx.} before PU rew."),
        ]
        if doReweighted:
            NvtxPlots.append(drawfw.PlotParams("_offlinePVCount", (0, 60), plotTitle="reconstructed N_{vtx.} after PU rew.(N_{true})",
                    weights=["PUWeightNtrue_puWeightProducer"]))

        for p in NvtxPlots:
            p.doChi2Test("t-channel", "mu", chi2options={"weight_type":"WW"})

        psMu += sigDataMuShapeComp.plot(cutlist.finalMu, NvtxPlots, cutDescription="muon channel, final sel.")

    if doWeights:
        allMCDataMu = plotfw.methods.SampleList()
        allMCDataMu.addGroup(smplsAllMC)
        allMCDataMu.addGroup(smplsMu)
        allMCDataMuShapeComp = drawfw.ShapePlotCreator(allMCDataMu, n_cores=1)
        psMu += allMCDataMuShapeComp.plot(cutlist.initial, NvtxPlots, cutDescription="skimmed MC")
        psMu += allMCDataMuShapeComp.plot(cutlist.finalMu, NvtxPlots, cutDescription="muon channel, final sel.")

        sigMainBKG = plotfw.methods.SampleList()
        sigMainBKG.addGroup(smpls.groups["t-channel"])
        sigMainBKG.addGroup(smpls.groups["TTbar"])
        sigMainBKG.addGroup(smpls.groups["WJets"])
        sigMainBKGComp = drawfw.ShapePlotCreator(sigMainBKG, n_cores=1)
        weightPlots = [
            drawfw.PlotParams("bTagWeight_bTagWeightProducer", (0.01, 10), doLogY=True, plotTitle="b-tag weight (nominal)"),
            drawfw.PlotParams("PUWeightNtrue_puWeightProducer", (0, 5), doLogY=True, plotTitle="PU weight (N_{true})"),
            drawfw.PlotParams("PUWeightN0_puWeightProducer", (0, 5), doLogY=True, plotTitle="PU weight (N_{0})")
        ]
        psMu += sigMainBKGComp.plot(cutlist.initial, weightPlots, cutDescription="skimmed MC")
        psMu += sigMainBKGComp.plot(cutlist.finalMu, weightPlots, cutDescription="muon channel, final sel.")

    ps = psMu + psEle
    i = 1
    ofdir = "plots_out_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4))
    os.mkdir(ofdir)
    for p in ps:
        p.save(fout=(ofdir + "/plot" + str(i)), fmt="pdf", log=True)
        i += 1
