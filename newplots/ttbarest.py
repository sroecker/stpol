# Confgure logging (has to be done before everything else)
import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
# Also log to file `ttbarest.log`
fileloghandler = logging.FileHandler('ttbarest.log')
fileloghandler.setLevel(logging.DEBUG)
fileloghandler.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(fileloghandler)

# Imports
from plotfw import drawfw
from plotfw.params import Cuts as cuts
from plotfw.params import Vars as variables
import samples

# Cuts
#cut = cuts.mu * cuts.mlnu * cuts.jetPt * cuts.jetRMS * cuts.etaLJ * cuts.jetEta * cuts.MTmu
cut = cuts.recoFState * cuts.mu * cuts.jetPt * cuts.jetRMS * cuts.jetEta * cuts.MTmu
cutlist = {
	'3J1T': cut * cuts.jets_3J1T,
	#'3J2T': cut * cuts.jets_3J2T,
}

# Set plots
weights   = ['PUWeightNtrue_puWeightProducer']
weights_b = weights+['bTagWeight_bTagWeightProducerNJMT']
weights = weights_b = None
plots = [
	drawfw.PlotParams(variables.cos_theta, (-1, 1), ymax=2300, ofname='costheta',   vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.cos_theta, (-1, 1), ymax=2300, ofname='costheta_b', vars_to_enable=None, weights=weights_b),

	drawfw.PlotParams(variables.top_mass, (100, 500), ymax=9000, bins=20, ofname='topmass',    vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.top_mass, (100, 500), ymax=9000, bins=20, ofname='topmass_b',  vars_to_enable=None, weights=weights_b),

	drawfw.PlotParams(variables.etalj, (0, 5),  ymax=5000, ofname='bjeteta',    vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.etalj, (0, 5),  ymax=5000, ofname='bjeteta_b',  vars_to_enable=None, weights=weights_b),
]

# Set up samples
samples.directory = '/scratch/morten/mar6_iso/'
samples.split_ttbar = False
samples.load()

for ck,c in cutlist.items():
	print 'Cut:', ck
	ps = samples.pltcMu.plot(c, plots)
	for p in ps:
		p.save(fout = 'plots_ttbar/ttbar_%s_%s'%(ck,p.getName()), fmt='pdf', log=True)
