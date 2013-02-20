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
    smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')

    #smplsgen.add('DYJets', 'DYJets', 'DYJets.root')

    smplsgen.add('QCD', 'QCDMu', 'QCDMu.root')

    smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_BCtoE.root')

    #smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_20_30_EMEnriched.root')
    #smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_30_80_EMEnriched.root')
    #smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'QCD_Pt_80_170_EMEnriched.root')
    ##FIXME: 170_250 is missing
    #smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_350_EMEnriched.root')

    smpls = smplsgen.getSampleList()

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

    #plotpars = [drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5))]
    plotparsMu1 = [drawfw.PlotParams('_muonsWithIso_0_relIso', (0, 1))]
    plotparsEle1 = [drawfw.PlotParams('_elesWithIso_0_relIso', (0, 1))]
    jetPlots = [drawfw.PlotParams('_lightJetCount + _bJetCount', (1, 6), bins=6, plotTitle="N_{jets} in muon channel")]
    finalSelPlots = [drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), plotTitle="#cos #theta_{lj} in muon channel, final selection")]

    psMu = []
    psEle = []
    #psMu = pltcMu.plot(cutlist.initial, plotparsMu1)
    #psMu += pltcMu.plot(cutlist.jets_OK*cutlist.mu, jetPlots)
    psMu += pltcMu.plot(cutlist.finalMu, finalSelPlots)
    #psEle = pltcEle.plot(cutlist.initial, plotparsEle1)
    #psEle2 = pltcEle.plot(cutlist.initial, plotparsEle2)

    #ps = psMu + psEle
    ps = psMu + psEle

    for p in ps:
        p.doLogY = True
        p.save()

