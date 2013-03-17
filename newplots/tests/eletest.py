import logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

testlog = logging.getLogger('eletest')
testlog_fh = logging.FileHandler('eletest.log')
testlog_fh.setLevel(logging.DEBUG)
testlog_fh.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
testlog.addHandler(testlog_fh)

from plotfw import drawfw, methods
from plotfw.params import Cuts as cuts, Vars as variables

# Set samples
directory = '/scratch/joosep/step2_Data_Iso_Mar15/'
smpls = [
	methods.DataSample('WD_SingleEleA1', 459, directory=directory),
	methods.DataSample('WD_SingleEleB', 459, directory=directory),
	methods.DataSample('WD_SingleEleC1', 459, directory=directory),
	methods.DataSample('WD_SingleEleC2', 459, directory=directory),
	methods.DataSample('WD_SingleEleD', 459, directory=directory),
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

for s in smpls:
	testlog.info('Sample `%s`', s.name)
	for cut in cuts:
		testlog.info('> cut: `%s`', str(cut))
		testlog.info('> > events: `%i`', s.cacheEntryList(cut))
	testlog.info('')
