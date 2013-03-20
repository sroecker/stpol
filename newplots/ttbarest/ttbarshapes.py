# Confgure logging (has to be done before everything else)
import logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s %(message)s')
# Also log to file `ttbarshapes.log`
fileloghandler = logging.FileHandler('ttbarshapes.log')
fileloghandler.setLevel(logging.DEBUG)
fileloghandler.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(fileloghandler)

# Imports
from plotfw import drawfw
from plotfw.params import Cuts as cuts
from plotfw.params import Vars as variables
from plotfw.params import colors

# Samples
path = '/scratch/joosep/step2_MC_Iso_Mar14/'

sample_fulllept = drawfw.methods.MCSample('WD_TTJets_FullLept', name='TTJets_FullLept', directory=path)
sample_semilept = drawfw.methods.MCSample('WD_TTJets_SemiLept', name='TTJets_SemiLept', directory=path)

samples = {}
samples['TTJets_FullLept'] = drawfw.methods.SampleGroup('TTJets_FullLept', colors['TTJets_FullLept'])
samples['TTJets_FullLept'].add(sample_fulllept)
samples['TTJets_SemiLept'] = drawfw.methods.SampleGroup('TTJets_SemiLept', colors['TTJets_SemiLept'])
samples['TTJets_SemiLept'].add(sample_semilept)
samples['TTbar'] = drawfw.methods.SampleGroup('TTbar', colors['TTbar'])
samples['TTJets_FullLept'].add(sample_fulllept)
samples['TTJets_SemiLept'].add(sample_semilept)

# Cuts
cut_std = cuts.recoFState * cuts.mu * cuts.jetPt * cuts.jetRMS * cuts.jetEta * cuts.MTmu
cut_sig = cuts.mlnu * cuts.etaLJ
cuts_jet = {
	'3J1T': cut_std * cuts.jets_3J1T,
	'3J2T': cut_std * cuts.jets_3J2T,
	'2J1T': cut_std * cuts.jets_2J1T,
}

# Set plots
weights = [variables.pu_weight, variables.b_weight["nominal"]]
plots = [
	drawfw.PlotParams(variables.cos_theta, (-1, 1), ofname='costheta', weights=weights),
	drawfw.PlotParams(variables.top_mass, (100, 500), bins=20, ofname='topmass', weights=weights),
	drawfw.PlotParams(variables.etalj, (0, 5), ofname='bjeteta', weights=weights),
]


for ck,c in cuts_jet.items():
	print 'Cut:', ck
	cuts = {
		'std': c,
		'sig': c * cut_sig
	}

	ps = []
	for sk,s in samples.items():
		logging.debug('Sample: %s', sk)
		ps += drawfw.SeparateCutShapePlotCreator(s, cuts).plot(plots)
	
	logging.debug('Plots: %s', str(ps))
	
	for p in ps:
		fout_fname = 'plots_ttbar/ttshp_%s_%s'%(ck,p.getName())
		logging.debug('Saving to: %s', fout_fname)
		p.save(fout = fout_fname, fmt='pdf', log=True)
