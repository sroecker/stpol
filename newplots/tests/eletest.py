import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from plotfw import drawfw, methods
from plotfw.params import Cuts as cuts, Vars as variables

# Set samples
smpls = [
	methods.DataSample('WD_SingleEleC1', 459, directory='/home/joosep/singletop/stpol/crabs/step2_Data_Iso_Mar11/')
]

# Set the cuts (all basic combinations of finalEle)
cuts = [
	cuts.recoFState,
	cuts.recoFState * cuts.ele,
	cuts.recoFState * cuts.Orso,
	cuts.recoFState * cuts.MTele,
	cuts.recoFState * cuts.ele    * cuts.Orso,
	cuts.recoFState * cuts.ele    * cuts.MTele,
	cuts.recoFState * cuts.Orso   * cuts.MTele,
	cuts.finalEle
]

for cut in cuts:
	print 'Cut:', str(cut)
	for s in smpls:
		print 'Events for %s:  %i'%(s.name, s.cacheEntryList(cut))
	print
