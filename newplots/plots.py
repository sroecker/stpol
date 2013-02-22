from plotfw import drawfw
from plotfw.params import Cuts as cutlist
import plotfw
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(message)s")
import pdb
from samples import *

#TODO: normalized QCD vs. signal comparison, data vs. MC for lepton relIso
if __name__ == "__main__":
#    datasmplsMu, datasmplsEle, smpls, pltcMu, pltcEle = initSamples()

    psMu = []
    psEle = []
    #Plot the lepton rel. iso distributions
    preLepPlotsMu = [
        drawfw.PlotParams('_muonsWithIso_0_relIso', (0, 0.2), plotTitle="muon rel. iso. before ID", doLogY=True),
    ]
    preLepPlotsEle = [
        drawfw.PlotParams('_elesWithIso_0_relIso', (0, 0.2), plotTitle="electron rel. iso. before ID", doLogY=True)
    ]
#    psMu += pltcMu.plot(cutlist.initial, preLepPlotsMu)
#    psEle += pltcEle.plot(cutlist.initial, preLepPlotsEle)

    #Plot the NJet distribution in the muon/ele channel
    jetPlots = [drawfw.PlotParams('_lightJetCount + _bJetCount', (1, 6), bins=6, plotTitle="N_{jets}", doLogY=True)]
#    psMu += pltcMu.plot(cutlist.jets_OK * cutlist.mu, jetPlots, cutDescription="mu channel")
    #psEle += pltcMu.plot(cutlist.jets_OK * cutlist.ele, jetPlots, cutDescription="ele channel")

    #Plot the N-bTag distribution in 2J
    jetPlots2J = [drawfw.PlotParams('_bJetCount', (0, 3), bins=4, plotTitle="N_{b-tags}", doLogY=True)]
    #psMu += pltcMu.plot(cutlist.jets_2J * cutlist.mu, jetPlots2J, cutDescription="mu channel")
    #psEle += pltcMu.plot(cutlist.jets_2J * cutlist.ele, jetPlots2J, cutDescription="ele channel, 2J")

    #MET/MtW distribution
    metPlotsMu = [drawfw.PlotParams('_muAndMETMT', (0, 150), plotTitle="M_{t}(W)")]
    metPlotsEle = [drawfw.PlotParams('_patMETs_0_Pt', (0, 150), plotTitle="MET")]
#    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J * cutlist.MTmu, metPlotsMu, cutDescription="mu channel, 2J")
    #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J * cutlist.MTele, metPlotsEle, cutDescription="ele. channel, 2J")

    #Plot b-discriminator of highest and lowest b-tagged jet in the muon channel
    jetbDiscrPlots = [
        #drawfw.PlotParams('_highestBTagJet_0_bDiscriminator', (0, 10), plotTitle="TCHP discriminator of the b-jet", doLogY=True),
        #drawfw.PlotParams('_lowestBTagJet_0_bDiscriminator', (0, 10), plotTitle="TCHP discriminator of the light jet", doLogY=True),
    ]
#    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J * cutlist.MTmu, jetbDiscrPlots, cutDescription="mu channel, 2J, M_{t}(W)>50 GeV")
    #psEle += pltcMu.plot(cutlist.ele * cutlist.jets_2J * cutlist.MTele, jetbDiscrPlots, cutDescription="ele channel, 2J, MET>45 GeV")

    #top mass plot
    topMassPlots = [
        drawfw.PlotParams('_recoTop_0_Mass', (100, 500), plotTitle="M_{bl#nu}"),
    ]
#    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J1T * cutlist.etaLJ * cutlist.MTmu, topMassPlots, cutDescription="mu channel, 2J1T, |#eta|_{lj}>2.5, M_{t}(W)>50 GeV")
    #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T, MET>45 GeV")

    #Light jet plots
    lightJetPlots = [
        drawfw.PlotParams('_lowestBTagJet_0_Eta', (-5, 5), plotTitle="#eta of the light jet"),
        drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5), plotTitle="|#eta| of the light jet"),
        drawfw.PlotParams('_lowestBTagJet_0_rms', (0, 0.15), plotTitle="rms of the light jet constituents", doLogY=True)
    ]
#    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J1T, lightJetPlots, cutDescription="mu channel, 2J1T")
    #psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T")

    #Plot cosTheta* etc in the final selection
    finalSelPlots = [drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), plotTitle="cos #theta_{lj} in muon channel, final selection")]
#    psMu += pltcMu.plot(cutlist.finalMu, finalSelPlots, cutDescription="mu channel, 2J1T, final selection")
    #psEle += pltcEle.plot(cutlist.finalEle, finalSelPlots, cutDescription="ele channel, 2J1T, final selection")

    sigQCD = plotfw.methods.SampleList()
    sigQCD.addGroup(smpls.groups["t-channel"])
    sigQCD.addGroup(smpls.groups["QCD"])
    sigQCDshapeComp = drawfw.ShapePlotCreator(sigQCD)
    #psMu += sigQCDshapeComp.plot(cutlist.initial, [drawfw.PlotParams("_muonsWithIso_0_relIso", (0, 0.5), doLogY=True)])

    sigDataMu = plotfw.methods.SampleList()
    sigDataMu.addGroup(smpls.groups["t-channel"])
    sigDataMu.addGroup(smplsMu)
    sigDataMuShapeComp = drawfw.ShapePlotCreator(sigDataMu)
    psMu += sigDataMuShapeComp.plot(cutlist.initial, [drawfw.PlotParams("_offlinePVCount", (0, 60))])

    ps = psMu + psEle
    for p in ps:
        p.save(fmt="pdf")
