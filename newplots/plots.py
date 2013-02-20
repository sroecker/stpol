from plotfw import drawfw
from plotfw.params import Cuts as cutlist
import logging
logging.basicConfig(level=logging.DEBUG)
#from IPython.core.display import Image

def initSamples():
    from newplots.plotfw import drawfw
    datasmplsMu = [
        drawfw.DataSample('SingleMuAB_5299_pb.root', 5299, name="SingleMuAB", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        drawfw.DataSample('SingleMuC_6790_pb.root', 6790, name="SingleMuC", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
        drawfw.DataSample('SingleMuD_7274_pb.root', 7247, name="SingleMuD", directory='/home/joosep/singletop/data/trees/Feb18/Iso'),
    ]
    datasmplsEle = [
        drawfw.DataSample('SingleEleD_7234_pb.root', 7234, directory='/home/joosep/singletop/data/trees/Feb18/Iso')
    ]
    smplsgen = drawfw.SampleListGenerator('/home/joosep/singletop/data/trees/Feb18/Iso/')
    smplsgen.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')
    smplsgen.add('t-channel', 'T_t', 'T_t.root')
    smplsgen.add('t-channel', 'Tbar_t', 'Tbar_t.root')
    smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')

    smplsgen.add('DYJets', 'DYJets', 'DYJets.root')

    smplsgen.add('QCD', 'QCDMu', 'QCDMu.root')

    smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_BCtoE.root')
    smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_BCtoE.root')

    smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_20_30_EMEnriched.root')
    smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_30_80_EMEnriched.root')
    smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'QCD_Pt_80_170_EMEnriched.root')
    #FIXME: 170_250 is missing
    smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_350_EMEnriched.root')

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


if __name__ == "__main__":
    datasmpls, smpls, pltcMu, pltcEle = initSamples()

    plotpars = [drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5))]


    psMu = pltcMu.plot(cutlist.mu, plotpars)
    psEle = pltcEle.plot(cutlist.ele, plotpars)

    ps = psMu + psEle
