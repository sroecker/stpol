from plotfw import drawfw

_directory = '/home/joosep/singletop/data/trees/Feb18/Iso'

datasmplsMu = [
	drawfw.DataSample('SingleMuAB_5299_pb.root', 5299, name="SingleMuAB", directory=_directory),
	#drawfw.DataSample('SingleMuC_6790_pb.root', 6790, name="SingleMuC", directory=_directory),
	#drawfw.DataSample('SingleMuD_7274_pb.root', 7247, name="SingleMuD", directory=_directory),
]

smplsMu = drawfw.SampleGroup("mu", ROOT.kBlack, "single mu")
smplsMu.addList(datasmplsMu)

datasmplsEle = [
	drawfw.DataSample('SingleEleA1_82_pb.root', 82, directory=_directory),
	drawfw.DataSample('SingleEleC1_495_pb.root', 495, directory=_directory),
	#drawfw.DataSample('SingleEleC2_6118_pb.root', 6118, directory=_directory),
	#drawfw.DataSample('SingleEleD_7234_pb.root', 7234, directory=_directory)
]
smplsEle = drawfw.SampleGroup("ele", ROOT.kBlack, "single ele")
smplsEle.addList(datasmplsEle)

smplsgen = drawfw.SampleListGenerator(_directory)
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
smplsgen.add('diboson', 'ZZ', 'ZZ.root')

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

pltcMu = drawfw.StackedPlotCreator(datasmplsMu, smpls)
pltcEle = drawfw.StackedPlotCreator(datasmplsEle, smpls)
