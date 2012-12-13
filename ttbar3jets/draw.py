#!/bin/env python
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='Creates plots of a dataset.')
parser.add_argument('-p', '--proc', default='test', choices=['3J1T', '3J2T', 'test'])
parser.add_argument('-t', '--optag', default=None)
parser.add_argument('-c', '--ctag', default=None, choices=[None,'TCHP'])
parser.add_argument('-d', '--data', default='A', choices=['A', 'AB'])

args = parser.parse_args() # with bad arguments the script stops here

# Start creating plots
import drawfw # here so it wont override argparse argument handling
print 'Running `%s` with optag %s'%(args.proc, args.optag)

chstring = 'p:%s, dt:%s'%(args.proc, args.data)
if args.optag is not None:
	chstring+= ', ot:%s'%args.optag
if args.ctag is not None:
	chstring+= ', ct:%s'%args.ctag

dc = drawfw.DrawCreator(chstring)

dc.addCut('_topCount == 1')
dc.addCut('_goodJets_0_Pt>60')
dc.addCut('_goodJets_1_Pt>60')
dc.addCut('_muAndMETMT>50')
dc.addCut('_untaggedJets_0_rms<0.025')

# Add data and MC
ctagstring = '_%s'%args.ctag if args.ctag is not None else ''

if args.proc == '3J1T':
	prefix='trees/stpol_'
	suffix='_3J1T.root' # 3J1T
elif args.proc == '3J2T':
	prefix='trees/stp%s_3J2T_'%ctagstring
	suffix='.root' # 3J2T
else: # otherwise take 3J1T
	prefix='trees/stpol_'
	suffix='_3J1T.root'

# Data
try:
	if args.data == 'A':
		dc.setData(prefix+'dataA'+suffix, 808.472)
	elif args.data == 'AB':
		dc.setData(prefix+'dataAB'+suffix, 5238) # from TWiki
	else:
		print 'Bad value: args.data=`%s`'%args.data
		print 'Exiting!'
		exit(2)
except IOError as e:
	print e
	print 'Exiting!'
	exit(1)

# MC
dc.addMC(prefix+'QCD'+suffix, 134.680, 'QCD', drawfw.ROOT.kGray)

dc.addMC(prefix+'wjets'+suffix, 36257.2, 'wjets', drawfw.ROOT.kGreen+3)
dc.addMC(prefix+'zjets'+suffix, 3503.71, 'zjets', drawfw.ROOT.kBlue+4)
dc.addMC(prefix+'WW'+suffix, 54.838, 'WW', drawfw.ROOT.kBlue+1)
dc.addMC(prefix+'WZ'+suffix, 32.3161, 'WZ', drawfw.ROOT.kBlue+1)
dc.addMC(prefix+'ZZ'+suffix, 8.059, 'ZZ', drawfw.ROOT.kBlue+1)
dc.addMC(prefix+'ttbar'+suffix, 234, 'ttbar', drawfw.ROOT.kOrange+7)

dc.addMC(prefix+'T_tW'+suffix, 11.1, 'T_tW', drawfw.ROOT.kYellow-6)
dc.addMC(prefix+'Tbar_tW'+suffix, 11.1, 'Tbar_tW', drawfw.ROOT.kYellow-6)
dc.addMC(prefix+'T_s'+suffix, 3.79, 'T_s', drawfw.ROOT.kYellow)
dc.addMC(prefix+'Tbar_s'+suffix, 1.76, 'Tbar_s', drawfw.ROOT.kYellow)
dc.addMC(prefix+'T_t'+suffix, 56.4, 'T_t', drawfw.ROOT.kRed)
dc.addMC(prefix+'Tbar_t'+suffix, 30.7, 'Tbar_t', drawfw.ROOT.kRed)

# Plotting
if args.proc == 'test':
	print 'Entering test mode!'
	p=dc.plot('_recoTop_0_Mass', 50, 650, 16, 'topmass')
	drawfw.TCanvas()
	p.draw()
	p.legend.Draw('SAME')
	raw_input()
else:
	drawfw.ROOT.gROOT.SetBatch(True)
	
	prefix='plots/plot_'
	postfix = '_' + args.proc
	if args.optag is not None:
		postfix += '_'+args.optag
	#postfix += '.png'
	
	#dc.plot('_recoTop_0_Mass', 50, 650, 16, 'topmass').save(prefix+'topmass'+postfix)
	#dc.plot('_lowestBTagJet_0_Eta', -5, 5, 16, 'jeteta').save(prefix+'jeteta'+postfix)
	#dc.plot('abs(_lowestBTagJet_0_Eta)', 0, 4.5, 16, 'abseta').save(prefix+'abseta'+postfix)
	#dc.plot('_recoTop_0_Pt', 0, 500, 16, 'toppt').save(prefix+'toppt'+postfix)
	
	#dc.plot('_goodJets_0_Pt', 60, 460, 16, 'L0Pt').save(prefix+'L0Pt'+postfix)
	#dc.plot('abs(_goodJets_0_Eta)', 0, 4.5, 16, 'L0Eta').save(prefix+'L0Eta'+postfix)
	#dc.plot('_goodJets_0_rms', 0, 0.03, 16, 'L0rms').save(prefix+'L0rms'+postfix)
	
	#dc.plot('_goodJets_1_Pt', 60, 460, 16, 'L1Pt').save(prefix+'L1Pt'+postfix)
	#dc.plot('abs(_goodJets_1_Eta)', 0, 4.5, 16, 'L1Eta').save(prefix+'L1Eta'+postfix)
	#dc.plot('_goodJets_1_rms', 0, 0.03, 16, 'L1rms').save(prefix+'L1rms'+postfix)
	
	#dc.plot('_goodJets_2_Pt', 0, 500, 16, 'L2Pt').save(prefix+'L2Pt'+postfix)
	#dc.plot('abs(_goodJets_2_Eta)', 0, 4.5, 16, 'L2Eta').save(prefix+'L2Eta'+postfix)
	#dc.plot('_goodJets_2_rms', 0, 0.03, 16, 'L2rms').save(prefix+'L2rms'+postfix)
	
	#dc.plot('cosThetaLightJet_cosTheta', -1, 1, 16, 'costheta').save(prefix+'costheta'+postfix)
	#dc.plot('cosThetaLightJet_cosTheta', -1, 1, 16, 'costheta_fx', True).save(prefix+'costheta_fx'+postfix)
