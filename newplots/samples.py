import re, logging, os
import ROOT

import plotfw
from plotfw import drawfw

# Parameters with reasonable defaults
#directory = '/home/joosep/singletop/data/trees/Feb28'
#directory = '/hdfs/local/joosep/stpol/trees/Mar6/Iso'
directory = '/home/joosep/singletop/data/trees/Mar6_1/Iso'
fulldata = True
split_ttbar = False

# Output variables
pltcMu = None
pltcEle = None
pltcMuTest = None
smplsAllMC = None

def load():
	global directory, fulldata, split_ttbar # parameters
	global pltcMu, pltcEle, pltcMuTest # output variables

	def auto_data_sample(fname):
		m=re.match('([A-Za-z0-9]*)_([0-9]*)_pb.root', fname)
		samplename = m.group(1)
		lumi = m.group(2)
		logging.debug('Matched in string `%s` - name:`%s`, lumi:`%s`', fname, samplename, lumi)

		return drawfw.DataSample(fname, lumi, name=samplename, directory=directory)

	# Data samples - load files, remove some if needed, create groups
	files=os.listdir(directory)
	r=re.compile('SingleMu(.*)')
	datasmplsMu = map(auto_data_sample, filter(r.match, files))
	r=re.compile('SingleEle(.*)')
	datasmplsEle = map(auto_data_sample, filter(r.match, files))

	if not fulldata:
		datasmplsMu = datasmplsMu[0:1]
		datasmplsEle = datasmplsEle[0:2]

	smplsMu = drawfw.SampleGroup("mu", ROOT.kBlack, "single mu")
	smplsMu.pretty_name = "single #mu^{#pm}"
	smplsMu.addList(datasmplsMu)
	smplsEle = drawfw.SampleGroup("ele", ROOT.kBlack, "single ele")
	smplsEle.addList(datasmplsEle)

	# Monte Carlo samples
	smplsgen = drawfw.SampleListGenerator(directory)

#smplsgen.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')
	smplsgen.add('TTJets_SemiLept' if split_ttbar else 'TTbar', 'TTJets_SemiLept', 'TTJets_SemiLept.root')
	smplsgen.add('TTJets_FullLept' if split_ttbar else 'TTbar', 'TTJets_FullLept', 'TTJets_FullLept.root')

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

	# add some pretty names
	if 'TTbar' in smpls.groups:
		smpls.groups['TTbar'].pretty_name = "t#bar{t} (#rightarrow ll, lj)"
	smpls.groups["WJets"].pretty_name = "W(#rightarrow l#nu) + jets(excl.)"
	smpls.groups["QCD"].pretty_name = "QCD (MC)"

	#Get WJets inclusive + exclusive samples
	smplsgenWJets = drawfw.SampleListGenerator(directory)
	smplsgenWJets.add('WJets_inclusive', 'WJets', 'WJets_inclusive.root')
	smplsgenWJets.add('W1Jets', 'W1Jets', 'W1Jets_exclusive.root')
	smplsgenWJets.add('W2Jets', 'W2Jets', 'W2Jets_exclusive.root')
	smplsgenWJets.add('W3Jets', 'W3Jets', 'W3Jets_exclusive.root')
	smplsgenWJets.add('W4Jets', 'W4Jets', 'W4Jets_exclusive.root')
	smplsWJets_all = smplsgenWJets.getSampleList()
	sample_WJets_exclusive = smplsWJets_all.groups["W1Jets"] + smplsWJets_all.groups["W2Jets"] + smplsWJets_all.groups["W3Jets"] + smplsWJets_all.groups["W4Jets"]
	sample_WJets_exclusive.pretty_name = "W(#rightarrow l#nu) + jets (excl.)"
	sample_WJets_exclusive.name = "WJets_exclusive"
	smplsWJets_all.groups["WJets_inclusive"].pretty_name = "W(#rightarrow l#nu) + jets (incl.)"
	smplsWJets_all.groups["WJets_inclusive"].name = "WJets_inclusive"
	sample_WJets_exclusive.color = ROOT.kRed
	smplsWJets_all.groups["WJets_inclusive"].color = ROOT.kBlue
	smplsWJets_incl_excl = plotfw.methods.SampleList()
	smplsWJets_incl_excl.addGroup(sample_WJets_exclusive)
	smplsWJets_incl_excl.addGroup(smplsWJets_all.groups["WJets_inclusive"])
	#smplsWJets_incl_excl.addGroup(smplsMu)

	smplsgenTTbar = drawfw.SampleListGenerator(directory)
	smplsgenTTbar.add('TTJets_SemiLept', 'TTJets_SemiLept', 'TTJets_SemiLept.root')
	smplsgenTTbar.add('TTJets_FullLept', 'TTJets_FullLept', 'TTJets_FullLept.root')
	smplsgenTTbar.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')
	smplsTTbar_all = smplsgenTTbar.getSampleList()
	smplsTTbar_exclusive = smplsTTbar_all.groups["TTJets_SemiLept"] + smplsTTbar_all.groups["TTJets_FullLept"]
	smplsTTbar_exclusive.name = "TTbar_exclusive"
	smplsTTbar_exclusive.pretty_name = "TTbar exclusive"
	smplsTTbar_exclusive.color = ROOT.kRed
	smplsTTbar_inclusive = smplsTTbar_all.groups["TTbar"]
	smplsTTbar_inclusive.name = "TTbar_inclusive"
	smplsTTbar_inclusive.pretty_name = "TTbar inclusive"
	smplsTTbar_inclusive.color = ROOT.kBlue
	smplsTTbar_incl_excl = plotfw.methods.SampleList()
	smplsTTbar_incl_excl.addGroup(smplsTTbar_exclusive)
	smplsTTbar_incl_excl.addGroup(smplsTTbar_inclusive)

	# Output the plotcreators
	pltcMu = drawfw.StackedPlotCreator(datasmplsMu, smpls)
	pltcEle = drawfw.StackedPlotCreator(datasmplsEle, smpls)

	# Test plotcreator
	#smplsTest = plotfw.methods.SampleList()
	#smplsTest.addGroup(smpls.groups['t-channel'])
	#if 'TTbar' in smpls.groups:
	#	smplsTest.addGroup(smpls.groups['TTbar'])
	#else:
	#	smplsTest.addGroup(smpls.groups['WJets'])
	#datasmplsMuTest = [auto_data_sample('SingleMuAB_5269_pb.root')]
	#pltcMuTest = drawfw.StackedPlotCreator(datasmplsMuTest, smplsTest)

	# All of MC
	#global smplsAllMC
	smplsAllMC = plotfw.methods.SampleGroup("allmc", ROOT.kRed, "full MC")
	for group in smpls.groups.values():
		smplsAllMC.samples += group.samples

	return smpls, smplsMu, smplsAllMC, smplsWJets_incl_excl, smplsTTbar_incl_excl
#=======
#import ROOT
#
##_directory = '/home/joosep/singletop/data/trees/Feb18/Iso'
#_directory = '/scratch/joosep/Feb28'
#
#datasmplsMu = [
#	drawfw.DataSample('SingleMuAB_5313_pb.root', 5313, name="SingleMuAB", directory=_directory),
#	drawfw.DataSample('SingleMuC_6790_pb.root', 6790, name="SingleMuC", directory=_directory),
#	drawfw.DataSample('SingleMuD_7274_pb.root', 7274, name="SingleMuD", directory=_directory),
#]
#
#smplsMu = drawfw.SampleGroup("mu", ROOT.kBlack, "single mu")
#smplsMu.pretty_name = "single #mu^{#pm}"
#smplsMu.addList(datasmplsMu)
#
#datasmplsEle = [
#	drawfw.DataSample('SingleEleA1_82_pb.root', 82, name="SingleEleA", directory=_directory),
#	drawfw.DataSample('SingleEleB_5231_pb.root', 5231, name="SingleEleB", directory=_directory),
#	drawfw.DataSample('SingleEleC1_495_pb.root', 495, name="SingleEleC1", directory=_directory),
#	drawfw.DataSample('SingleEleC2_6118_pb.root', 6118, name="SingleEleC2", directory=_directory),
#	drawfw.DataSample('SingleEleD_7234_pb.root', 7234, name="SingleEleD", directory=_directory)
#]
#smplsEle = drawfw.SampleGroup("ele", ROOT.kBlack, "single ele")
#smplsEle.addList(datasmplsEle)
#
#smplsgen = plotfw.methods.SampleListGenerator(_directory)
##smplsgen.add('TTbar', 'TTbar', 'TTJets_MassiveBinDECAY.root')
#smplsgen.add('TTbar', 'TTJets_FullLept', 'TTJets_FullLept.root')
#smplsgen.add('TTbar', 'TTJets_SemiLept', 'TTJets_SemiLept.root')
#
#smplsgen.add('t-channel', 'T_t', 'T_t.root')
#smplsgen.add('t-channel', 'Tbar_t', 'Tbar_t.root')
#smplsgen.add('s-channel', 'T_s', 'T_s.root')
#smplsgen.add('s-channel', 'Tbar_s', 'Tbar_s.root')
#smplsgen.add('tW-channel', 'T_tW', 'T_tW.root')
#smplsgen.add('tW-channel', 'Tbar_tW', 'Tbar_tW.root')
#
##smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')
#smplsgen.add('WJets', 'W1Jets', 'W1Jets_exclusive.root')
#smplsgen.add('WJets', 'W2Jets', 'W2Jets_exclusive.root')
#smplsgen.add('WJets', 'W3Jets', 'W3Jets_exclusive.root')
#smplsgen.add('WJets', 'W4Jets', 'W4Jets_exclusive.root')
#
#smplsgen.add('DYJets', 'DYJets', 'DYJets.root')
#
#smplsgen.add('diboson', 'WW', 'WW.root')
#smplsgen.add('diboson', 'WZ', 'WZ.root')
#smplsgen.add('diboson', 'ZZ', 'ZZ.root')
#
#smplsgen.add('QCD', 'QCDMu', 'QCDMu.root')
#
#smplsgen.add('QCD', 'GJets1', 'GJets1.root')
#smplsgen.add('QCD', 'GJets2', 'GJets2.root')
#
#smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'QCD_Pt_20_30_BCtoE.root')
#smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'QCD_Pt_30_80_BCtoE.root')
#smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'QCD_Pt_80_170_BCtoE.root')
#smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'QCD_Pt_170_250_BCtoE.root')
#smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'QCD_Pt_250_350_BCtoE.root')
#smplsgen.add('QCD', 'QCD_Pt_350_BCtoE', 'QCD_Pt_350_BCtoE.root')
#
#smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'QCD_Pt_20_30_EMEnriched.root')
#smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'QCD_Pt_30_80_EMEnriched.root')
#smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'QCD_Pt_80_170_EMEnriched.root')
#smplsgen.add('QCD', 'QCD_Pt_170_250_EMEnriched', 'QCD_Pt_170_250_EMEnriched.root')
#smplsgen.add('QCD', 'QCD_Pt_250_350_EMEnriched', 'QCD_Pt_250_350_EMEnriched.root')
#smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'QCD_Pt_350_EMEnriched.root')
#
#smpls = smplsgen.getSampleList()
#smpls.groups["TTbar"].pretty_name = "t#bar{t} (#rightarrow ll, lj)"
#smpls.groups["WJets"].pretty_name = "W(#rightarrow l#nu) + jets(inc.)"
#smpls.groups["QCD"].pretty_name = "QCD (MC)"
#
#for sample in smpls.groups["QCD"].samples:
#	sample.disabled_weights = ["bTagWeight_bTagWeightProducer"]
#
#pltcMu = drawfw.StackedPlotCreator(datasmplsMu, smpls)
#pltcEle = drawfw.StackedPlotCreator(datasmplsEle, smpls)
#
##smplsTest = plotfw.methods.SampleList()
##smplsTest.addGroup(smpls.groups["t-channel"])
##smplsTest.addGroup(smpls.groups["TTbar"])
##datasmplsMuTest = [
##	drawfw.DataSample('SingleMuAB_5269_pb.root', 5269, name="SingleMuAB", directory=_directory)
##]
##pltcMuTest = drawfw.StackedPlotCreator(datasmplsMuTest, smplsTest)
#
#smplsAllMC = plotfw.methods.SampleGroup("allmc", ROOT.kRed, "full MC")
#for group in smpls.groups.values():
#	smplsAllMC.samples += group.samples
#>>>>>>> new samples
