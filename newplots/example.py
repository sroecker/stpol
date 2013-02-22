from plotfw import drawfw
from plotfw.params import Cuts as cutlist

# Set samples
datasmpl = drawfw.DataSample('WD_SingleMuAB_4665_pb.root', 4665, directory='/home/joosep/singletop/data/trees/Feb8_A/Iso')

smplsgen = drawfw.SampleListGenerator('/home/joosep/singletop/data/trees/Feb8_A/Iso')
smplsgen.add('Diboson', 'WW', 'WD_WW.root')
smplsgen.add('Diboson', 'WZ', 'WD_WZ.root')
smplsgen.add('Diboson', 'ZZ', 'WD_ZZ.root')
smplsgen.add('TTbar', 'TTbar', 'WD_TTbar.root')
smplsgen.add('WJets', 'W1Jets', 'W1Jets.root')
smplsgen.add('WJets', 'W2Jets', 'W2Jets.root')
smplsgen.add('WJets', 'W3Jets', 'W3Jets.root')
smplsgen.add('WJets', 'W4Jets', 'W4Jets.root')
smplsgen.add('T', 'T_t', 'WD_T_t.root')
smplsgen.add('T', 'T_s', 'WD_T_s.root')
smplsgen.add('T', 'T_tW', 'WD_T_tW.root')
smplsgen.add('Tbar', 'Tbar_t', 'WD_Tbar_t.root')
smplsgen.add('Tbar', 'Tbar_s', 'WD_Tbar_s.root')
smplsgen.add('Tbar', 'Tbar_tW', 'WD_Tbar_tW.root')
smpls = smplsgen.getSampleList()

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
