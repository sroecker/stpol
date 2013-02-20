from plotfw import drawfw
from plotfw.params import Cuts as cuts

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s;%(levelname)s;%(message)s")

# 3J1T cut
cut = cuts.mu * cuts.mlnu * cuts.jets_3J1T * cuts.jetPt * cuts.jetRMS * cuts.etaLJ * cuts.jetEta * cuts.MTmu

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (130, 220), bins=9),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (2.5, 4.5)),
	#drawfw.PlotParams('_lowestBTagJet_0_Eta', (-5, 5)),
	drawfw.PlotParams('_recoTop_0_Pt', (0, 300), bins=15),
	drawfw.PlotParams('cosThetaLightJet_cosTheta', (-1, 1))
]

from samples import pltcMu

ps = pltcMu.plot(cut, plots)

for p in ps:
	p.save(fout = 'ttbar_%s'%p.getName())
