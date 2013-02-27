import plotfw
from plotfw import drawfw

import ROOT

#_directory = '/home/joosep/singletop/data/trees/Feb18/Iso'
_directory = '/scratch/joosep/Iso'

datasmplsMu = [
	drawfw.DataSample('SingleMuAB_5269_pb.root', 5269, name="SingleMuAB", directory=_directory),
	drawfw.DataSample('SingleMuC_6655_pb.root', 6655, name="SingleMuC", directory=_directory),
	drawfw.DataSample('SingleMuD_7104_pb.root', 7104, name="SingleMuD", directory=_directory),
]

smplsMu = drawfw.SampleGroup("mu", ROOT.kBlack, "single mu")
smplsMu.addList(datasmplsMu)

datasmplsEle = [
	drawfw.DataSample('SingleEleA1_82_pb.root', 82, name="SingleEleA", directory=_directory),
	drawfw.DataSample('SingleEleB_5125_pb.root', 5125, name="SingleEleB", directory=_directory),
	drawfw.DataSample('SingleEleC1_495_pb.root', 495, name="SingleEleC1", directory=_directory),
	drawfw.DataSample('SingleEleC2_5938_pb.root', 5938, name="SingleEleC2", directory=_directory),
	drawfw.DataSample('SingleEleD_7002_pb.root', 7002, name="SingleEleD", directory=_directory)
]
smplsEle = drawfw.SampleGroup("ele", ROOT.kBlack, "single ele")
smplsEle.addList(datasmplsEle)

smplsgen = plotfw.methods.SampleListGenerator(_directory)
#smplsgen.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')
smplsgen.add('TTbar', 'TTJets_FullLept', 'TTJets_FullLept.root')
smplsgen.add('TTbar', 'TTJets_SemiLept', 'TTJets_SemiLept.root')

smplsgen.add('t-channel', 'T_t', 'T_t.root')
smplsgen.add('t-channel', 'Tbar_t', 'Tbar_t.root')
smplsgen.add('s-channel', 'T_s', 'T_s.root')
smplsgen.add('s-channel', 'Tbar_s', 'Tbar_s.root')
smplsgen.add('tW-channel', 'T_tW', 'T_tW.root')
smplsgen.add('tW-channel', 'Tbar_tW', 'Tbar_tW.root')

#smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')
smplsgen.add('WJets', 'W1Jets', 'W1Jets_exclusive.root')
smplsgen.add('WJets', 'W2Jets', 'W2Jets_exclusive.root')
smplsgen.add('WJets', 'W3Jets', 'W3Jets_exclusive.root')
smplsgen.add('WJets', 'W4Jets', 'W4Jets_exclusive.root')

smplsgen.add('DYJets', 'DYJets', 'DYJets.root')

smplsgen.add('diboson', 'WW', 'WW.root')
smplsgen.add('diboson', 'WZ', 'WZ.root')
smplsgen.add('diboson', 'ZZ', 'ZZ.root')

smplsgen.add('QCD', 'QCDMu', 'QCDMu.root')

smplsgen.add('QCD', 'GJets1', 'GJets1.root')
smplsgen.add('QCD', 'GJets2', 'GJets2.root')

smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_BCtoE.root')
smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_BCtoE.root')
smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_BCtoE.root')
smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_BCtoE.root')
smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_BCtoE.root')
smplsgen.add('QCD', 'QCD_Pt_350_BCtoE', 'QCD_Pt_350_BCtoE.root')

smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_20_30_EMEnriched.root')
smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_30_80_EMEnriched.root')
smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'QCD_Pt_80_170_EMEnriched.root')
smplsgen.add('QCD', 'QCD_Pt_170_250_EMEnriched', 'QCD_Pt_170_250_EMEnriched.root')
smplsgen.add('QCD', 'QCD_Pt_250_350_EMEnriched', 'QCD_Pt_250_350_EMEnriched.root')
smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_350_EMEnriched.root')

smpls = smplsgen.getSampleList()
smpls.groups["TTbar"].pretty_name = "t#bar{t} (#rightarrow ll, lj)"
smpls.groups["WJets"].pretty_name = "W(#rightarrow l#nu) + jets(inc.)"

for sample in smpls.groups["QCD"].samples:
	sample.disabled_weights = ["bTagWeight_bTagWeightProducer"]

pltcMu = drawfw.StackedPlotCreator(datasmplsMu, smpls)
pltcEle = drawfw.StackedPlotCreator(datasmplsEle, smpls)

smplsTest = plotfw.methods.SampleList()
smplsTest.addGroup(smpls.groups["t-channel"])
smplsTest.addGroup(smpls.groups["TTbar"])
datasmplsMuTest = [
	drawfw.DataSample('SingleMuAB_5269_pb.root', 5269, name="SingleMuAB", directory=_directory)
]
pltcMuTest = drawfw.StackedPlotCreator(datasmplsMuTest, smplsTest)

smplsAllMC = plotfw.methods.SampleGroup("allmc", ROOT.kRed, "full MC")
for group in smpls.groups.values():
	smplsAllMC.samples += group.samples
