from plotfw import drawfw
from plotfw.drawfw import addAutoSample as addSample
from plotfw.params import Cuts as cutlist

# Set samples
datasmpl = drawfw.DataSample('WD_SingleMuAB_4665_pb.root', 4665, directory='/home/joosep/singletop/data/trees/Feb8_A/Iso')

smpls = drawfw.SampleList('/home/joosep/singletop/data/trees/Feb8_A/Iso')
addSample(smpls, 'Diboson', 'WW', 'WD_WW.root')
addSample(smpls, 'Diboson', 'WZ', 'WD_WZ.root')
addSample(smpls, 'Diboson', 'ZZ', 'WD_ZZ.root')
addSample(smpls, 'TTbar', 'TTbar', 'WD_TTbar.root')
addSample(smpls, 'WJets', 'W1Jets', 'W1Jets.root')
addSample(smpls, 'WJets', 'W2Jets', 'W2Jets.root')
addSample(smpls, 'WJets', 'W3Jets', 'W3Jets.root')
addSample(smpls, 'WJets', 'W4Jets', 'W4Jets.root')
addSample(smpls, 'T', 'T_t', 'WD_T_t.root')
addSample(smpls, 'T', 'T_s', 'WD_T_s.root')
addSample(smpls, 'T', 'T_tW', 'WD_T_tW.root')
addSample(smpls, 'Tbar', 'Tbar_t', 'WD_Tbar_t.root')
addSample(smpls, 'Tbar', 'Tbar_s', 'WD_Tbar_s.root')
addSample(smpls, 'Tbar', 'Tbar_tW', 'WD_Tbar_tW.root')

smpls.listSamples() # print sample list

# Set the cut
#cut = drawfw.methods.Cut('', '')
cut = cutlist.finalMu
print 'Cut:', str(cut)

# Set plots
plots = [
	drawfw.PlotParams('_recoTop_0_Mass', (130, 220)),
	drawfw.PlotParams('abs(_lowestBTagJet_0_Eta)', (2.5, 4.5))
]

# Plot
pltc = drawfw.StackedPlotCreator(datasmpl, smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
