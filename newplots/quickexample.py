from plotfw import drawfw
from plotfw.drawfw import addAutoSample as addSample
from plotfw.params import Cuts as cutlist

# Set samples
datasmpl = drawfw.DataSample('WD_SingleEleA1_82_pb.root', 82, directory='/home/joosep/singletop/data/trees/Feb8_A/Iso')

smpls = drawfw.SampleList('/home/joosep/singletop/data/trees/Feb8_A/Iso')
addSample(smpls, 'WJets', 'W1Jets', 'W1Jets.root')
addSample(smpls, 'WJets', 'W2Jets', 'W2Jets.root')
addSample(smpls, 'WJets', 'W3Jets', 'W3Jets.root')
addSample(smpls, 'WJets', 'W4Jets', 'W4Jets.root')
addSample(smpls, 'TTbar', 'TTbar', 'WD_TTbar.root')

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
pltc = drawfw.StackedPlotCreator(datasmpl, smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
