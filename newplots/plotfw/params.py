import logging, re, copy
import ROOT
from cross_sections import xs

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
		super(CutF,self).__init__(cutname, cutstring, vars)

class CutP(Cut):
	"""Parses the variable name automatically.
	
	It assumes that the variable name is the leftmost one."""
	def __init__(self, cutname, cutstring):
		m=re.match('([A-Za-z0-9_]*)[ ]*([><=]*)[ ]*(.*)', cutstring)
		logging.debug('In `%s` matching for `%s`', cutstring, m.group(1))
		super(CutP,self).__init__(cutname, cutstring, [m.group(1)])

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

	recoFState = CutP('recoFstate', '_topCount==1')
	mu  = CutP('mu', '_muonCount==1') \
	    * CutP('muIso', '_goodSignalMuons_0_relIso<0.12') \
	    * CutP('looseMuVeto', '_looseVetoMuCount==0') \
	    * CutP('looseEleVeto', '_looseVetoEleCount==0') \

	ele = CutP('ele', '_electronCount==1') \
	    * CutP('eleIso', '_goodSignalElectrons_0_relIso<0.3') \
	    * CutP('eleMVA', '_goodSignalElectrons_0_mvaID>0.9') \

	muonID = CutP(None, '_muonsWithIso_0_normChi2 > 10') \
	       * CutP(None, '_muonsWithIso_0_track_hitPattern_trackerLayersWithMeasurement > 5') \
	       * CutP(None, '_muonsWithIso_0_globalTrack_hitPattern_numberOfValidMuonHits > 0') \
	       * CutP(None, '_muonsWithIso_0_innerTrack_hitPattern_numberOfValidPixelHits > 0') \
	       * CutF(None, 'abs({0}) > 0.2', ['_muonsWithIso_0_db']) \
	       * CutF(None, 'abs({0}) > 0.5', ['_muonsWithIso_0_dz']) \
	       * CutP(None, '_muonsWithIso_0_numberOfMatchedStations > 1')

	muonPt  = CutP('muonPt',  '_muonsWithIso_0_Pt > 26')
	muonEta = CutF('muonEta', 'abs({0}) < 2.1', ['_muonsWithIso_0_Eta'])
	muonIso = CutP('muonIso', '_muonsWithIso_0_relIso < 0.12')

	jets_1LJ = CutP('1LJ', '_lightJetCount==1')
	jets_OK = CutP(None, '_lightJetCount>=0') \
	        * CutP(None, '_bJetCount>=0')
	jets_2plusJ = jets_OK * CutF('2plusLJ', '({0} + {1})>=2', ['_lightJetCount', '_bJetCount'])
	jets_2J = jets_OK * CutF('2J', '({0} + {1})==2', ['_lightJetCount', '_bJetCount'])
	jets_2J1T = CutP(None, '_lightJetCount==1') * CutP(None, '_bJetCount==1')
	jets_2J0T = CutP(None, '_lightJetCount==2') * CutP(None, '_bJetCount==0')
	jets_3J1T = CutP(None, '_lightJetCount==2') * CutP(None, '_bJetCount==1')
	jets_3J2T = CutP(None, '_lightJetCount==2') * CutP(None, '_bJetCount==2')
	realSol = CutP('realSol', 'solType_recoNuProducerMu==0')
	cplxSol = CutP('cplxSol', 'solType_recoNuProducerMu==1')
	mlnu = CutP(None, '_recoTop_0_Mass>130') * CutP(None, '_recoTop_0_Mass<220')
	etaLJ = CutF('#eta_{lj}', 'abs({0})>2.5', ['_lowestBTagJet_0_Eta'])
	sidebandRegion = invert(mlnu) #sidebandRegion = Cut('!ml#nu', '!(_recoTop_0_Mass>130&&_recoTop_0_Mass<220)')
	jetPt = CutP(None, '_goodJets_0_Pt>40') * CutP(None, '_goodJets_1_Pt>40')
	jetEta = Cut('jetEta', 'abs({0})<4.5 && abs({1})<4.5', ['_lowestBTagJet_0_Eta', '_highestBTagJet_0_Eta'])
	jetRMS = CutP('rms_{lj}', '_lowestBTagJet_0_rms < 0.025')
	MTmu = CutP('MT', '_muAndMETMT > 50')
	MTele = CutP('MT', '_patMETs_0_Pt>45')

Cuts.muonID.rename('muonID')
Cuts.jets_OK.rename('jetsOK')
Cuts.jets_2J1T.rename('2J1T')
Cuts.jets_2J0T.rename('2J0T')
Cuts.jets_3J1T.rename('3J1T')
Cuts.jets_3J2T.rename('3J2T')
Cuts.mlnu.rename('ml#nu')
Cuts.sidebandRegion.rename('!ml#nu')
Cuts.jetPt.rename('jetPt')
