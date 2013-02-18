import logging
from plotfw import drawfw
from plotfw.params import Cuts as cutlist

# Logging
logging.basicConfig(level=logging.DEBUG)

# Set samples
directory = '/home/joosep/singletop/data/trees/Feb18/Iso'

datasmpls = [
	drawfw.DataSample( 'SingleEleA1_82_pb.root',  82, directory=directory),
	drawfw.DataSample('SingleEleC1_495_pb.root', 495, directory=directory)
]

smplsgen = drawfw.SampleListGenerator(directory)
smplsgen.add('WJets', 'WJets', 'WJets_inclusive.root')
smplsgen.add('Diboson', 'WW', 'WW.root')
smplsgen.add('Diboson', 'WZ', 'WZ.root')
#smplsgen.add('Diboson', 'ZZ', 'ZZ.root')
#smplsgen.add('WJets', 'W1Jets', 'W1Jets.root')
#smplsgen.add('WJets', 'W2Jets', 'W2Jets.root')
#smplsgen.add('WJets', 'W3Jets', 'W3Jets.root')
#smplsgen.add('WJets', 'W4Jets', 'W4Jets.root')
#smplsgen.add('TTbar', 'TTbar', 'WD_TTbar.root')
smpls = smplsgen.getSampleList()

smpls.listSamples() # print sample list

# Set the cut
cut = drawfw.methods.Cut('ab_topmass', '_recoTop_0_Mass > 200 && _recoTop_0_Mass < 500') \
    * cutlist.ele
#cut = cutlist.finalEle
print 'Cut:', str(cut)

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (0, 500)),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 4.5))
]

# Plot
pltc = drawfw.StackedPlotCreator(datasmpls, smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
