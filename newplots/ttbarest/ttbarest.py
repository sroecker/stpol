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
weights = [variables.pu_weight]
weights_b = weights + [variables.b_weight["nominal"]]

plots = [
	drawfw.PlotParams(variables.cos_theta, (-1, 1), ofname='costheta',   vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.cos_theta, (-1, 1), ofname='costheta_b', vars_to_enable=None, weights=weights_b),

	drawfw.PlotParams(variables.top_mass, (100, 500), bins=20, ofname='topmass',	vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.top_mass, (100, 500), bins=20, ofname='topmass_b',  vars_to_enable=None, weights=weights_b),

	drawfw.PlotParams(variables.etalj, (0, 5), ofname='bjeteta',	vars_to_enable=None, weights=weights),
	drawfw.PlotParams(variables.etalj, (0, 5), ofname='bjeteta_b',  vars_to_enable=None, weights=weights_b),
]

# Set up samples
samples.directory_mc = '/testhome/jooseptest/step2_MC_Iso_Mar14'
samples.directory_data = '/testhome/jooseptest/step2_Data_Iso_Mar15'
samples.split_ttbar = False
samples.load()

for ck,c in cutlist.items():
	print 'Cut:', ck
	samples.pltcMu.set_n_cores(10)
	#samples.pltcMu.frac_entries=1.0
	ps = samples.pltcMu.plot(c, plots)
	for p in ps:
		p.save(fout = 'plots_ttbar/ttbar_%s_%s'%(ck,p.getName()), fmt='pdf', log=True)
