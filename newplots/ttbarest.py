from plotfw import drawfw
from plotfw.params import Cuts as cuts

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(message)s")

# Cuts
cut = cuts.mu * cuts.mlnu * cuts.jetPt * cuts.jetRMS * cuts.etaLJ * cuts.jetEta * cuts.MTmu
cutlist = {
	'3J1T': cut * cuts.jets_3J1T,
	'3J2T': cut * cuts.jets_3J2T,
}

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (130, 220), bins=9, ofname='topmass'),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (2.5, 4.5), ofname='bjeteta'),
	#drawfw.PlotParams('_lowestBTagJet_0_Eta', (-5, 5)),
	drawfw.PlotParams('_recoTop_0_Pt', (0, 300), bins=15, ofname='toppt'),
	drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1), ofname='costheta')
]

from samples import pltcMu

for ck,c in cutlist.items():
	print 'Cut:', ck
	ps = pltcMu.plot(c, plots)
	for p in ps:
		p.save(fout = 'plots_ttbar/ttbar_%s_%s'%(ck,p.getName()), fmt='pdf', log=True)
