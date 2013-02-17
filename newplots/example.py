from plotfw import drawfw
from plotfw.drawfw import addAutoSample as addSample
from plotfw.params import Cuts as cutlist

# Set samples
smpls = drawfw.SampleList('/home/joosep/singletop/data/trees/Feb8_A/Iso')
addSample(smpls, 'Dilepton', 'WW', 'WD_WW.root')
addSample(smpls, 'Dilepton', 'WZ', 'WD_WZ.root')
addSample(smpls, 'Dilepton', 'ZZ', 'WD_ZZ.root')
addSample(smpls, 'TTbar', 'TTbar', 'WD_TTbar.root')

smpls.listSamples()

datasmpl = drawfw.DataSample('WD_SingleMuAB_4665_pb.root', 4665, directory='/home/joosep/singletop/data/trees/Feb8_A/Iso')

# Set the cut
#cut = drawfw.methods.Cut('', '')
cut = cutlist.finalMu
print 'Cut:', str(cut)

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (50, 650)),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (0, 4.5))
]

# Plot
pltc = drawfw.StackedPlotCreator(datasmpl, smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
