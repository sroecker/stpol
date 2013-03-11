import logging, re, copy
import ROOT
from cross_sections import xs

def parent_branch(v):
	return v.split(".")[0] + "*"

# Class to handle (concatenate) cuts
class Cut(object):
	"""Class that handles cuts.

	Not only does it store information about cuts, it also implements
	methods to concatenate cuts together properly."""

	def __init__(self, cutName, cutStr, relvars=[]):
		self.cutName = str(cutName)
		self.cutStr = str(cutStr)

		if relvars is None:
			self._vars = set()
			logging.debug('No relevant variables in cut `%s` (cutstring: `%s`)!', cutName, cutStr)
		elif len(relvars)==0:
			self._vars = set()
			logging.warning('No relevant variables in cut `%s` (cutstring `%s`)!', cutName, cutStr)
		else:
			self._vars = set(relvars)

		logging.debug('Created cut `%s`: `%s`, `%s`', self.cutName, self.cutStr, self._vars)
		#self.cutSequence = [copy.deepcopy(self)]

	def __mul__(self, other):
		cutName = self.cutName + ' & ' + other.cutName
		cutStr = '('+self.cutStr+') && ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr, self._vars|other._vars)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __add__(self, other):
		cutName = self.cutName + ' | ' + other.cutName
		cutStr = '('+self.cutStr+') || ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr, self._vars|other._vars)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __str__(self):
		return self.cutName

	def __repr__(self):
		return self.cutName

	def getUsedVariables(self):
		return list(self._vars)

	def rename(self, name):
		logging.debug('Renaming `%s` to `%s` (cutstring: `%s`)', self.cutName, name, self.cutStr)
		self.cutName = name

	def invert(self):
		logging.debug('Inverting `%s` (`%s`)', self.cutName, self.cutStr)
		self.cutStr = '!({0})'.format(self.cutStr)
		logging.debug('Inverted: `%s`', self.cutStr)

class CutF(Cut):
	"""Cut with string formatting

	Use the {} string formatting syntax to create cutstring. Allows
	for the automatic storing of relevant variables."""
	def __init__(self, cutname, cutformatstring, vars):
		cutstring = cutformatstring.format(*vars)
		vars = [v.split(".")[0] for v in vars]
		super(CutF,self).__init__(cutname, cutstring, vars)

class CutP(Cut):
	"""Parses the variable name automatically.

	It assumes that the variable name is the leftmost one."""
	def __init__(self, cutname, cutstring):
		#m=re.match('([A-Za-z0-9_]*)[ ]*([><=]*)[ ]*(.*)', cutstring)
		m=re.match('([^><=]*)[ ]*([><=]*)[ ]*(.*)', cutstring)
		logging.debug('In `%s` matching for `%s`', cutstring, m.group(1))
		super(CutP,self).__init__(cutname, cutstring, [parent_branch(m.group(1))])

def invert(cut):
	ret = copy.deepcopy(cut)
	ret.invert()
	return ret

colors = {
	'T_t': ROOT.kRed,
	'Tbar_t': ROOT.kRed,
	'T_tW': ROOT.kYellow+4,
	'Tbar_tW': ROOT.kYellow+4,
	'T_s': ROOT.kYellow,
	'Tbar_s': ROOT.kYellow,

	'DYJets': ROOT.kViolet,

	'WJets': ROOT.kGreen,
	'W1Jets': ROOT.kGreen+1,
	'W2Jets': ROOT.kGreen+2,
	'W3Jets': ROOT.kGreen+3,
	'W4Jets': ROOT.kGreen+4,

	'WW': ROOT.kBlue,
	'WZ': ROOT.kBlue,
	'ZZ': ROOT.kBlue,

	'TTbar': ROOT.kOrange,
	'TTJets_FullLept': ROOT.kOrange+1,
	'TTJets_SemiLept': ROOT.kOrange+2,

	'QCDMu': ROOT.kGray,
	'GJets1': ROOT.kGray,
	'GJets2': ROOT.kGray,

	'QCD_Pt_20_30_EMEnriched': ROOT.kGray,
	'QCD_Pt_30_80_EMEnriched': ROOT.kGray,
	'QCD_Pt_80_170_EMEnriched': ROOT.kGray,
	'QCD_Pt_170_250_EMEnriched': ROOT.kGray,
	'QCD_Pt_250_350_EMEnriched': ROOT.kGray,
	'QCD_Pt_350_EMEnriched': ROOT.kGray,


	'QCD_Pt_20_30_BCtoE': ROOT.kGray,
	'QCD_Pt_30_80_BCtoE': ROOT.kGray,
	'QCD_Pt_80_170_BCtoE': ROOT.kGray,
	'QCD_Pt_170_250_BCtoE': ROOT.kGray,
	'QCD_Pt_250_350_BCtoE': ROOT.kGray,
	'QCD_Pt_350_BCtoE': ROOT.kGray,

	'SingleMu': ROOT.kBlack,
	'SingleEle': ROOT.kBlack,
}

# Selection applied as in https://indico.cern.ch/getFile.py/access?contribId=1&resId=0&materialId=slides&confId=228739
class Cuts:
	initial = Cut('postSkim', '1==1', relvars = None)

	recoFState = CutP('recoFstate', 'int_topCount__STPOLSEL2.obj==1')
	mu  = CutP('mu', 'int_muonCount__STPOLSEL2.obj==1') \
		* CutP('muIso', 'floats_goodSignalMuonsNTupleProducer_relIso_STPOLSEL2.obj[0]<0.12') \
		* CutP('looseMuVeto', 'int_looseVetoMuCount__STPOLSEL2.obj==0') \
		* CutP('looseEleVeto', 'int_looseVetoEleCount__STPOLSEL2.obj==0') \

	ele = CutP('ele', 'int_electronCount__STPOLSEL2.obj==1') \
		* CutP('eleIso', 'floats_goodSignalElectronsNTupleProducer_relIso_STPOLSEL2.obj[0]<0.3') \
		* CutP('eleMVA', 'floats_goodSignalElectronsNTupleProducer_mvaID_STPOLSEL2.obj[0]>0.9') \

	muonID = CutP(None, 'floats_goodSignalMuonsNTupleProducer_normChi2_STPOLSEL2.obj[0] > 10') \
		   * CutP(None, 'floats_goodSignalMuonsNTupleProducer_trackhitPatterntrackerLayersWithMeasurement_STPOLSEL2.obj[0] > 5') \
		   * CutP(None, 'floats_goodSignalMuonsNTupleProducer_innerTrackhitPatternnumberOfValidPixelHits_STPOLSEL2.obj[0] > 0') \
		   * CutP(None, 'floats_goodSignalMuonsNTupleProducer_globalTrackhitPatternnumberOfValidMuonHits_STPOLSEL2.obj> 0') \
		   * CutF(None, 'abs({0}) > 0.2', ['floats_goodSignalMuonsNTupleProducer_db_STPOLSEL2.obj[0]']) \
		   * CutF(None, 'abs({0}) > 0.5', ['floats_goodSignalMuonsNTupleProducer_dz_STPOLSEL2.obj[0]']) \
		   * CutP(None, 'floats_goodSignalMuonsNTupleProducer_numberOfMatchedStations_STPOLSEL2.obj[0] > 1')

	muonPt  = CutP('muonPt',  'floats_goodSignalMuonsNTupleProducer_Pt_STPOLSEL2.obj[0] > 26')
	muonEta = CutF('muonEta', 'abs({0}) < 2.1', ['floats_goodSignalMuonsNTupleProducer_Eta_STPOLSEL2.obj[0]'])
	muonIso = CutP('muonIso', 'floats_goodSignalMuonsNTupleProducer_relIso_STPOLSEL2.obj[0] < 0.12')

	jets_1LJ = CutP('1LJ', 'int_lightJetCount__STPOLSEL2.obj ==1')
	jets_OK = CutP(None, 'int_lightJetCount__STPOLSEL2.obj>=0') \
			* CutP(None, 'int_bJetCount__STPOLSEL2.obj>=0')
	jets_2plusJ = jets_OK * CutF('2plusLJ', '({0} + {1})>=2', ['int_lightJetCount__STPOLSEL2.obj', 'int_bJetCount__STPOLSEL2.obj'])
	jets_2J = jets_OK * CutF('2J', '({0} + {1})==2', ['int_lightJetCount__STPOLSEL2.obj', 'int_bJetCount__STPOLSEL2.obj'])
	jets_3J = jets_OK * CutF('3J', '({0} + {1})==3', ['int_lightJetCount__STPOLSEL2.obj', 'int_bJetCount__STPOLSEL2.obj'])
	jets_2J1T = CutP(None, 'int_lightJetCount__STPOLSEL2.obj==1') * CutP(None, 'int_bJetCount__STPOLSEL2.obj==1')
	jets_2J0T = CutP(None, 'int_lightJetCount__STPOLSEL2.obj==2') * CutP(None, 'int_bJetCount__STPOLSEL2.obj==0')
	jets_3J1T = CutP(None, 'int_lightJetCount__STPOLSEL2.obj==2') * CutP(None, 'int_bJetCount__STPOLSEL2.obj==1')
	jets_3J0T = CutP(None, 'int_lightJetCount__STPOLSEL2.obj==3') * CutP(None, 'int_bJetCount__STPOLSEL2.obj==0')
	jets_3J2T = CutP(None, 'int_lightJetCount__STPOLSEL2.obj==1') * CutP(None, 'int_bJetCount__STPOLSEL2.obj==2')
	#realSol = CutP('realSol', 'solType_recoNuProducerMu==0')
	#cplxSol = CutP('cplxSol', 'solType_recoNuProducerMu==1')
	mlnu = CutP(None, 'floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]>130') * CutP(None, 'floats_recoTopNTupleProducer_Mass_STPOLSEL2.obj[0]<220')
	etaLJ = CutF('#eta_{lj}', 'abs({0})>2.5', ['floats_lowestBTagJetNTupleProducer_Eta_STPOLSEL2.obj[0]'])
	sidebandRegion = invert(mlnu) #sidebandRegion = Cut('!ml#nu', '!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)')
	jetPt = CutP(None, 'floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[0]>40') * CutP(None, 'floats_goodJetsNTupleProducer_Pt_STPOLSEL2.obj[1]>40')
	jetEta = CutF('jetEta', 'abs({0})<4.5 && abs({1})<4.5', ['floats_lowestBTagJetNTupleProducer_Eta_STPOLSEL2.obj[0]', 'floats_highestBTagJetNTupleProducer_Eta_STPOLSEL2.obj[0]'])
	jetRMS = CutP('rms_{lj}', 'floats_lowestBTagJetNTupleProducer_rms_STPOLSEL2.obj[0] < 0.025')
	MTmu = CutP('MT', 'double_muAndMETMT__STPOLSEL2.obj > 50')
	MTele = CutP('MT', 'floats_patMETNTupleProducer_Eta_STPOLSEL2.obj[0]>45')

	#Orso = mlnu * jets_2J1T * jetPt * jetRMS * MT * etaLJ#jetEta
	Orso = mlnu * jets_2J1T * jetPt * jetRMS * etaLJ * jetEta
	finalMu = mu * recoFState * Orso * MTmu
	finalEle = ele * recoFState * Orso * MTele

Cuts.muonID.rename('muonID')
Cuts.jets_OK.rename('jetsOK')
Cuts.jets_2J1T.rename('2J1T')
Cuts.jets_2J0T.rename('2J0T')
Cuts.jets_3J1T.rename('3J1T')
Cuts.jets_3J2T.rename('3J2T')
Cuts.mlnu.rename('ml#nu')
Cuts.sidebandRegion.rename('!ml#nu')
Cuts.jetPt.rename('jetPt')

class Var:
	def __init__(self, var, name=None, units=None):
		self.var = var
		self.name = name if name is not None else var
		self.units = units if units is not None else "u"
	def __str__(self):
		return self.name + "(" + self.var + ")"


class Vars:
	cos_theta = Var("double_cosTheta_cosThetaLightJet_STPOLSEL2.obj", "cos #theta_{lj}")
	b_weight = dict()
	b_weight["nominal"] = Var("double_bTagWeightProducerNJMT_bTagWeight_STPOLSEL2.obj", "b-weight (nominal)")
