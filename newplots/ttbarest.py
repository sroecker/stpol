from plotfw import drawfw
from plotfw.params import Cuts as cuts
import samples

import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
# Also log to file `ttbarest.log`
fileloghandler = logging.FileHandler('ttbarest.log')
fileloghandler.setLevel(logging.DEBUG)
fileloghandler.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(fileloghandler)

# Cuts
#cut = cuts.mu * cuts.mlnu * cuts.jetPt * cuts.jetRMS * cuts.etaLJ * cuts.jetEta * cuts.MTmu
cut = cuts.recoFState * cuts.mu * cuts.jetPt * cuts.jetRMS * cuts.jetEta * cuts.MTmu
cutlist = {
	'3J1T': cut * cuts.jets_3J1T,
	'3J2T': cut * cuts.jets_3J2T,
}

# Set plots
enabled_vars = ['*']
weights   = ["PUWeightNtrue_puWeightProducer"]
weights_b = weights+["bTagWeight_bTagWeightProducer"]
#weights = None
plots = [
	drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), ofname='costheta',   vars_to_enable=enabled_vars, weights=weights),
	drawfw.PlotParams('_recoTop_0_Mass', (0, 500), bins=20, ofname='topmass',    vars_to_enable=enabled_vars, weights=weights),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5),  ofname='bjeteta',    vars_to_enable=enabled_vars, weights=weights),
	drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), ofname='costheta_b', vars_to_enable=enabled_vars, weights=weights_b),
	drawfw.PlotParams('_recoTop_0_Mass', (0, 500), bins=20, ofname='topmass_b',  vars_to_enable=enabled_vars, weights=weights_b),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 5),  ofname='bjeteta_b',  vars_to_enable=enabled_vars, weights=weights_b),
	#drawfw.PlotParams('_recoTop_0_Mass', (130, 220), bins=9, ofname='topmass', vars_to_enable=enabled_vars, weights=weights),
	#drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (2.5, 4.5), ofname='bjeteta', vars_to_enable=enabled_vars, weights=weights),
	#drawfw.PlotParams('_recoTop_0_Pt', (0, 300), bins=15, ofname='toppt', vars_to_enable=enabled_vars, weights=weights),
]

# Set up samples
samples.split_ttbar = True
samples.load()

for ck,c in cutlist.items():
	print 'Cut:', ck
	ps = samples.pltcMu.plot(c, plots)
	for p in ps:
		p.save(fout = 'plots_ttbar/ttbar_%s_%s'%(ck,p.getName()), fmt='pdf', log=True)