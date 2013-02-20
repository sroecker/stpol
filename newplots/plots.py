from plotfw import drawfw
from plotfw.params import Cuts as cutlist
import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(message)s")
import pdb

#from IPython.core.display import Image

def initSamples():
    from plotfw import drawfw
    datasmplsMu = [
        drawfw.DataSample('SingleMuAB_5299_pb.root', 5299, name="SingleMuAB", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        #drawfw.DataSample('SingleMuC_6790_pb.root', 6790, name="SingleMuC", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        #drawfw.DataSample('SingleMuD_7274_pb.root', 7247, name="SingleMuD", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
    ]
    datasmplsEle = [
        drawfw.DataSample('SingleEleA1_82_pb.root', 82, directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        drawfw.DataSample('SingleEleC1_495_pb.root', 495, directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        #drawfw.DataSample('SingleEleC2_6118_pb.root', 6118, directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        #drawfw.DataSample('SingleEleD_7234_pb.root', 7234, directory='/home/joosep/singletop/data/trees/Feb18/Iso')

    ]
    smplsgen = drawfw.SampleListGenerator('/home/joosep/singletop/data/trees/Feb18/Iso/')
    smplsgen.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')

    smplsgen.add('t-channel', 'T_t', 'T_t.root')
    smplsgen.add('t-channel', 'Tbar_t', 'Tbar_t.root')
    smplsgen.add('s-channel', 'T_s', 'T_s.root')
    smplsgen.add('s-channel', 'Tbar_s', 'Tbar_s.root')
    smplsgen.add('tW-channel', 'T_tW', 'T_tW.root')
    smplsgen.add('tW-channel', 'Tbar_tW', 'Tbar_tW.root')

    smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')

    smplsgen.add('DYJets', 'DYJets', 'DYJets.root')

    smplsgen.add('diboson', 'WW', 'WW.root')
    smplsgen.add('diboson', 'WZ', 'WZ.root')
    ##FIXME: ZZ is missing

    smplsgen.add('QCD', 'QCDMu', 'QCDMu.root')

    smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_BCtoE.root')

    smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_20_30_EMEnriched.root')
    smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_30_80_EMEnriched.root')
    smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'QCD_Pt_80_170_EMEnriched.root')
    ##FIXME: 170_250 is missing
    smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_350_EMEnriched.root')

    smpls = smplsgen.getSampleList()
    smpls.groups["TTbar"].prettyName = "t #bar{t}"

#    enabledBranches = ["_lowestBTagJet_0_Eta", "_muonCount", "_electronCount", "_goodSignal*", "_looseVeto*Count", "_lightJetCount"]
#    for i in range(len(datasmpls)):
#        datasmpls[i].tree.SetBranchStatus("*", 0)
#        for eb in enabledBranches:
#            datasmpls[i].tree.SetBranchStatus(eb, 1)
#    for group in smpls.groups.values():
#        for sample in group.samples:
#            sample.tree.SetBranchStatus("*", 0)
#            for eb in enabledBranches:
#                sample.tree.SetBranchStatus(eb, 1)
    pltcMu = drawfw.StackedPlotCreator(datasmplsMu, smpls)
    pltcEle = drawfw.StackedPlotCreator(datasmplsEle, smpls)

    return datasmplsMu, datasmplsEle, smpls, pltcMu, pltcEle

#TODO: normalized QCD vs. signal comparison, data vs. MC for lepton relIso
if __name__ == "__main__":
    datasmplsMu, datasmplsEle, smpls, pltcMu, pltcEle = initSamples()



    psMu = []
    psEle = []
    #Plot the lepton rel. iso distributions
    preLepPlotsMu = [
        drawfw.PlotParams('_muonsWithIso_0_relIso', (0, 0.2), plotTitle="muon rel. iso. before ID", doLogY=True),
    ]
    preLepPlotsEle = [
        drawfw.PlotParams('_elesWithIso_0_relIso', (0, 0.2), plotTitle="electron rel. iso. before ID", doLogY=True)
    ]
    psMu += pltcMu.plot(cutlist.initial, preLepPlotsMu)
    psEle += pltcEle.plot(cutlist.initial, preLepPlotsEle)

    #Plot the NJet distribution in the muon channel
    jetPlots = [drawfw.PlotParams('_lightJetCount + _bJetCount', (1, 6), bins=6, plotTitle="N_{jets}")]
    psMu += pltcMu.plot(cutlist.jets_OK*cutlist.mu, jetPlots)

    #Plot the NJet distribution in the muon channel
    jetPlots = [drawfw.PlotParams('_lightJetCount + _bJetCount', (1, 6), bins=6, plotTitle="N_{jets}")]
    psMu += pltcMu.plot(cutlist.jets_OK*cutlist.mu, jetPlots, cutDescription="mu channel")

    #MET/MtW distribution
    metPlotsMu = [drawfw.PlotParams('_muAndMETMT', (0, 150), plotTitle="M_{tW}")]
    metPlotsEle = [drawfw.PlotParams('_patMETs_0_Pt', (0, 150), plotTitle="MET")]
    psMu += pltcMu.plot(cutlist.mu*cutlist.jets_2J, metPlotsMu, cutDescription="mu channel, 2J")
    psEle += pltcEle.plot(cutlist.ele*cutlist.jets_2J, metPlotsEle, cutDescription="ele. channel, 2J")

    #Plot b-discriminator of highest and lowest b-tagged jet in the muon channel
    jetbDiscrPlots = [
        #drawfw.PlotParams('_highestBTagJet_0_bDiscriminator', (0, 10), plotTitle="TCHP discriminator of the b-jet", doLogY=True),
        #drawfw.PlotParams('_lowestBTagJet_0_bDiscriminator', (0, 10), plotTitle="TCHP discriminator of the light jet", doLogY=True),
    ]
    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J, jetbDiscrPlots, cutDescription="mu channel, 2J")
    psEle += pltcMu.plot(cutlist.ele * cutlist.jets_2J, jetbDiscrPlots, cutDescription="ele channel, 2J")

    lightJetPlots = [
        drawfw.PlotParams('_lowestBTagJet_0_Eta', (-5, 5), plotTitle="#eta of the light jet"),
        drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5), plotTitle="|#eta| of the light jet"),
        drawfw.PlotParams('_lowestBTagJet_0_rms', (0, 0.15), plotTitle="rms of the light jet constituents", doLogY=True)
    ]
    psMu += pltcMu.plot(cutlist.mu * cutlist.jets_2J1T, lightJetPlots, cutDescription="mu channel, 2J1T")
    psEle += pltcEle.plot(cutlist.ele * cutlist.jets_2J1T, lightJetPlots, cutDescription="ele. channel, 2J1T")

    #Plot cosTheta* etc in the final selection
    finalSelPlots = [drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), plotTitle="#cos #theta_{lj} in muon channel, final selection")]
    psMu += pltcMu.plot(cutlist.finalMu, finalSelPlots, cutDescription="mu channel, 2J1T")
    psEle += pltcEle.plot(cutlist.finalEle, finalSelPlots, cutDescription="ele channel, 2J1T")

    ps = psMu + psEle

    for p in ps:
        p.save()
