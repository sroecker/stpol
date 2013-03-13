import logging
from plotfw import drawfw
import plotfw.params as cuts

# Logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
# Also log to file `shapeexample.log`
fileloghandler = logging.FileHandler('shapeexample.log')
fileloghandler.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(fileloghandler)

# Set samples
directory = '/scratch/morten/mar6_iso/'

smplsgen = drawfw.SampleListGenerator(directory)
smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')
smplsgen.add('Diboson', 'WW', 'WW.root')
smplsgen.add('Diboson', 'WZ', 'WZ.root')
smpls = smplsgen.getSampleList()

smpls.listSamples() # print sample list

# Set the cut
cut = cuts.CutF('ab_topmass', '{0} > 200 && {0} < 500', ['_lightJetCount']) \
	* cuts.Cuts.ele

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (0, 500)),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 4.5))
]

# Plot
pltc = drawfw.ShapePlotCreator(smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
