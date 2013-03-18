import re, logging, os
import ROOT

import plotfw
from plotfw import drawfw

# Parameters with reasonable defaults
#directory_mc   = '/scratch/joosep/step2_MC_Iso_Mar14/'
#directory_data = '/scratch/joosep/step2_Data_Iso_Mar15/'
directory_mc   = '/home/joosep/singletop/stpol/crabs/step2_MC_Iso_Mar14/'
directory_data = '/home/joosep/singletop/stpol/crabs/step2_Data_Iso_Mar15'
fulldata = True
split_ttbar = False

# Output variables
pltcMu = None
pltcEle = None
pltcMuTest = None
smplsAllMC = None

def _parseLumis(directory):
	fname = directory + '/overview'
	logging.debug('Opening `%s` for lumi data.', fname)

	lumis = {}
	for ln in open(fname):
		ln = ln.split('|')
		if len(ln)==7:
			sample = ln[1].strip()
			lumi = float(ln[4])
			logging.debug('Lumi of `%s` = %f', sample, lumi)
			lumis[sample] = lumi
	return lumis

def load():
	global directory_mc, directory_data, fulldata, split_ttbar # parameters
	global pltcMu, pltcEle, pltcMuTest # output variables

	# Data samples - load files, remove some if needed, create groups
	files=os.listdir(directory_data)
	luminosities = _parseLumis(directory_data)

	def auto_data_sample(fname):
		#global luminosities
		m=re.match('WD_(SingleEle|SingleMu)([A-Z0-9]*)', fname)
		samplename = m.group(1) + m.group(2)
		lumi = luminosities[fname]
		logging.debug('Matched in string `%s` - name:`%s`, lumi:`%s`', fname, samplename, str(lumi))

		return drawfw.DataSample(fname, lumi, name=samplename, directory=directory_data)

	r=re.compile('WD_SingleMu(.*)')
	datasmplsMu = map(auto_data_sample, filter(r.match, files))
	r=re.compile('WD_SingleEle(.*)')
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
	smplsgen = drawfw.SampleListGenerator(directory_mc)

	smplsgen.add('TTJets_SemiLept' if split_ttbar else 'TTbar', 'TTJets_SemiLept', 'WD_TTJets_SemiLept')
	smplsgen.add('TTJets_FullLept' if split_ttbar else 'TTbar', 'TTJets_FullLept', 'WD_TTJets_FullLept')

	smplsgen.add('t-channel', 'T_t', 'WD_T_t')
	smplsgen.add('t-channel', 'Tbar_t', 'WD_Tbar_t')
	smplsgen.add('s-channel', 'T_s', 'WD_T_s')
	smplsgen.add('s-channel', 'Tbar_s', 'WD_Tbar_s')
	smplsgen.add('tW-channel', 'T_tW', 'WD_T_tW')
	smplsgen.add('tW-channel', 'Tbar_tW', 'WD_Tbar_tW')

	#smplsgen.add('WJets', 'WJets', 'WD_WJets_inclusive')
	smplsgen.add('WJets', 'W1Jets', 'WD_W1Jets_exclusive')
	smplsgen.add('WJets', 'W2Jets', 'WD_W2Jets_exclusive')
	smplsgen.add('WJets', 'W3Jets', 'WD_W3Jets_exclusive')
	smplsgen.add('WJets', 'W4Jets', 'WD_W4Jets_exclusive')

	smplsgen.add('DYJets', 'DYJets', 'WD_DYJets')

	smplsgen.add('diboson', 'WW', 'WD_WW')
	smplsgen.add('diboson', 'WZ', 'WD_WZ')
	smplsgen.add('diboson', 'ZZ', 'WD_ZZ')

	smplsgen.add('QCD', 'QCDMu', 'WD_QCDMu')

	smplsgen.add('QCD', 'GJets1', 'WD_GJets1')
	smplsgen.add('QCD', 'GJets2', 'WD_GJets2')

	smplsgen.add('QCD', 'QCD_Pt_20_30_BCtoE', 'WD_QCD_Pt_20_30_BCtoE')
	smplsgen.add('QCD', 'QCD_Pt_30_80_BCtoE', 'WD_QCD_Pt_30_80_BCtoE')
	smplsgen.add('QCD', 'QCD_Pt_80_170_BCtoE', 'WD_QCD_Pt_80_170_BCtoE')
	smplsgen.add('QCD', 'QCD_Pt_170_250_BCtoE', 'WD_QCD_Pt_170_250_BCtoE')
	smplsgen.add('QCD', 'QCD_Pt_250_350_BCtoE', 'WD_QCD_Pt_250_350_BCtoE')
	smplsgen.add('QCD', 'QCD_Pt_350_BCtoE', 'WD_QCD_Pt_350_BCtoE')

	smplsgen.add('QCD', 'QCD_Pt_20_30_EMEnriched', 'WD_QCD_Pt_20_30_EMEnriched')
	smplsgen.add('QCD', 'QCD_Pt_30_80_EMEnriched', 'WD_QCD_Pt_30_80_EMEnriched')
	smplsgen.add('QCD', 'QCD_Pt_80_170_EMEnriched', 'WD_QCD_Pt_80_170_EMEnriched')
	smplsgen.add('QCD', 'QCD_Pt_170_250_EMEnriched', 'WD_QCD_Pt_170_250_EMEnriched')
	smplsgen.add('QCD', 'QCD_Pt_250_350_EMEnriched', 'WD_QCD_Pt_250_350_EMEnriched')
	smplsgen.add('QCD', 'QCD_Pt_350_EMEnriched', 'WD_QCD_Pt_350_EMEnriched')

	smpls = smplsgen.getSampleList()

	# add some pretty names
	if 'TTbar' in smpls.groups:
		smpls.groups['TTbar'].pretty_name = "t#bar{t} (#rightarrow ll, lj)"
	smpls.groups["WJets"].pretty_name = "W(#rightarrow l#nu) + jets(excl.)"
	smpls.groups["QCD"].pretty_name = "QCD (MC)"
	for sample in smpls.groups["QCD"].samples:
		sample.disabled_weights += ["*"]
	#for sample in smpls.getSamples()
	#	sample.disabled_weights += ["PUWeightNtrue_puWeightProducer"]

	#Get WJets inclusive + exclusive samples
	smplsgenWJets = drawfw.SampleListGenerator(directory_mc)
	smplsgenWJets.add('WJets_inclusive', 'WJets', 'WD_WJets_inclusive')
	smplsgenWJets.add('W1Jets', 'W1Jets', 'WD_W1Jets_exclusive')
	smplsgenWJets.add('W2Jets', 'W2Jets', 'WD_W2Jets_exclusive')
	smplsgenWJets.add('W3Jets', 'W3Jets', 'WD_W3Jets_exclusive')
	smplsgenWJets.add('W4Jets', 'W4Jets', 'WD_W4Jets_exclusive')
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

	smplsgenTTbar = drawfw.SampleListGenerator(directory_mc)
	smplsgenTTbar.add('TTJets_SemiLept', 'TTJets_SemiLept', 'WD_TTJets_SemiLept')
	smplsgenTTbar.add('TTJets_FullLept', 'TTJets_FullLept', 'WD_TTJets_FullLept')
	smplsgenTTbar.add('TTbar', 'TTbar', 'WD_TTJets_MassiveBinDECAY')
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
	pltcMu = drawfw.StackPlotCreator(datasmplsMu, smpls)
	pltcEle = drawfw.StackPlotCreator(datasmplsEle, smpls)

	# Test plotcreator
	#smplsTest = plotfw.methods.SampleList()
	#smplsTest.addGroup(smpls.groups['t-channel'])
	#if 'TTbar' in smpls.groups:
	#	smplsTest.addGroup(smpls.groups['TTbar'])
	#else:
	#	smplsTest.addGroup(smpls.groups['WJets'])
	#datasmplsMuTest = [auto_data_sample('WD_SingleMuAB_5269_pb')]
	#pltcMuTest = drawfw.StackedPlotCreator(datasmplsMuTest, smplsTest)

	# All of MC
	#global smplsAllMC
	smplsAllMC = plotfw.methods.SampleGroup("allmc", ROOT.kRed, "full MC")
	for group in smpls.groups.values():
		smplsAllMC.samples += group.samples

	return smpls, smplsMu, smplsAllMC, smplsWJets_incl_excl, smplsTTbar_incl_excl
