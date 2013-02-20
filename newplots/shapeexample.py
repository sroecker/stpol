import logging
from plotfw import drawfw
from plotfw.params import Cuts as cutlist

# Logging
logging.basicConfig(filename='shapeexample.log', level=logging.DEBUG)

# Set samples
directory = '/home/joosep/singletop/data/trees/Feb18/Iso'

smplsgen = drawfw.SampleListGenerator(directory)
smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')
smplsgen.add('Diboson', 'WW', 'WW.root')
smplsgen.add('Diboson', 'WZ', 'WZ.root')
smpls = smplsgen.getSampleList()

smpls.listSamples() # print sample list

# Set the cut
cut = drawfw.methods.Cut('ab_topmass', '_recoTop_0_Mass > 200 && _recoTop_0_Mass < 500') \
	* cutlist.ele

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
