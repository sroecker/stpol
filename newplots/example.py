from plotfw import drawfw
from plotfw.drawfw import addAutoSample as addSample

# Set samples
smpls = drawfw.SampleList('/home/joosep/singletop/data/trees/Feb8_A/Iso')
addSample(smpls, 'Dilepton', 'WW', 'WD_WW.root')
addSample(smpls, 'Dilepton', 'WZ', 'WD_WZ.root')
addSample(smpls, 'Dilepton', 'ZZ', 'WD_ZZ.root')
addSample(smpls, 'TTbar', 'TTbar', 'WD_TTbar.root')

# Set cuts
#cuts = drawfw.params.Cuts.Orso
cuts = [drawfw.methods.Cut('', '')]
print 'Cuts:', cuts

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (50, 650))
]

# Plot
pltc = drawfw.StackedPlotCreator(smpls)
for c in cuts:
	pltc.plot(c, plots)
