import logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from plotfw import drawfw, methods
from plotfw.params import Cuts as cuts, Vars as variables

# Set samples
datasmpl = methods.DataSample('WD_SingleEleC1', 459, directory='/home/joosep/singletop/stpol/crabs/step2_Data_Iso_Mar11/')

smplsgen = methods.SampleListGenerator('/home/joosep/singletop/stpol/crabs/step2_MC_Iso_Mar11/')
#smplsgen.add('TTbar', 'TTJets_SemiLept', 'WD_TTJets_SemiLept')
#smplsgen.add('TTbar', 'TTJets_FullLept', 'WD_TTJets_FullLept')
smplsgen.add('t-channel', 'T_t', 'WD_T_t')
#smplsgen.add('t-channel', 'Tbar_t', 'WD_Tbar_t')
smplsgen.add('s-channel', 'T_s', 'WD_T_s')
#smplsgen.add('s-channel', 'Tbar_s', 'WD_Tbar_s')
smplsgen.add('tW-channel', 'T_tW', 'WD_T_tW')
#smplsgen.add('tW-channel', 'Tbar_tW', 'WD_Tbar_tW')
#smplsgen.add('WJets', 'W1Jets', 'WD_W1Jets_exclusive')
#smplsgen.add('WJets', 'W2Jets', 'WD_W2Jets_exclusive')
#smplsgen.add('WJets', 'W3Jets', 'WD_W3Jets_exclusive')
#smplsgen.add('WJets', 'W4Jets', 'WD_W4Jets_exclusive')
smpls = smplsgen.getSampleList()

smpls.listSamples() # print sample list

# Set the cut
#cut = drawfw.methods.Cut('', '')
cut = cuts.finalEle
print 'Cut:', str(cut)

# Set plots
plots = [
	drawfw.PlotParams(variables.top_mass, (130, 220)),
	drawfw.PlotParams(variables.etalj, (2.5, 4.5))
]

# Plot
pltc = drawfw.StackPlotCreator(datasmpl, smpls)
ps = pltc.plot(cut, plots)

for p in ps:
	p.save()
