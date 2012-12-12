#!/bin/env python
import argparse

# Argument parsing
parser = argparse.ArgumentParser(description='Creates plots of a dataset.')
parser.add_argument('-p', '--proc', default='test', choices=['3J1T', '3J2T', 'test'])
parser.add_argument('-t', '--optag', default=None)
parser.add_argument('-d', '--data', default='A', choices=['A', 'AB'])

args = parser.parse_args() # with bad arguments the script stops here

# Start creating plots
import drawfw # here so it wont override argparse argument handling
print 'Running `%s` with optag %s'%(args.proc, args.optag)

chstring = 'p:%s, dt:%s'%(args.proc, args.data)
if args.optag is not None:
	chstring+= ', ot:%s'%args.optag

dc = drawfw.DrawCreator(chstring)

dc.addCut('_topCount == 1')
dc.addCut('_goodJets_0_Pt>60')
dc.addCut('_goodJets_1_Pt>60')
dc.addCut('_muAndMETMT>50')

# Add data and MC
if args.proc == '3J1T':
	prefix='trees/stpol_'; suffix='_3J1T.root' # 3J1T
elif args.proc == '3J2T':
	prefix='trees/stp_3J2T_'; suffix='.root' # 3J2T
else:
	prefix='trees/stpol_'; suffix='_3J1T.root' # otherwise take 3J1T

# Data
try:
	if args.data == 'A':
		dc.setData(prefix+'dataA'+suffix, 808.472)
	elif args.data == 'AB':
		dc.setData(prefix+'dataAB'+suffix, 808.472)
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
dc.addMC(prefix+'zjets'+suffix, 3503.71, 'zjets', drawfw.ROOT.kOrange+7)
dc.addMC(prefix+'WW'+suffix, 54.838, 'WW', drawfw.ROOT.kBlue)
dc.addMC(prefix+'WZ'+suffix, 32.3161, 'WZ', drawfw.ROOT.kBlue)
dc.addMC(prefix+'ZZ'+suffix, 8.059, 'ZZ', drawfw.ROOT.kBlue)
dc.addMC(prefix+'ttbar'+suffix, 234, 'ttbar', drawfw.ROOT.kOrange+7)

dc.addMC(prefix+'T_t'+suffix, 56.4, 'T_t', drawfw.ROOT.kRed)
dc.addMC(prefix+'Tbar_t'+suffix, 30.7, 'Tbar_t', drawfw.ROOT.kRed)
dc.addMC(prefix+'T_s'+suffix, 3.79, 'T_s', drawfw.ROOT.kRed)
dc.addMC(prefix+'Tbar_s'+suffix, 1.76, 'Tbar_s', drawfw.ROOT.kRed)
dc.addMC(prefix+'T_tW'+suffix, 11.1, 'T_tW', drawfw.ROOT.kRed)
dc.addMC(prefix+'Tbar_tW'+suffix, 11.1, 'Tbar_tW', drawfw.ROOT.kRed)

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
	postfix += '.png'
	
	dc.plot('_recoTop_0_Mass', 50, 650, 16, 'topmass').save(prefix+'topmass'+postfix)
	dc.plot('_lowestBTagJet_0_Eta', -5, 5, 16, 'jeteta').save(prefix+'jeteta'+postfix)
	dc.plot('abs(_lowestBTagJet_0_Eta)', 0, 4.5, 16, 'abseta').save(prefix+'abseta'+postfix)
	dc.plot('_recoTop_0_Pt', 0, 500, 16, 'toppt').save(prefix+'toppt'+postfix)
