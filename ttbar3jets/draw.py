#!/bin/env python
import drawfw, sys

dc = drawfw.DrawCreator()

dc.addCut('_topCount == 1')
dc.addCut('_goodJets_0_Pt>60')
dc.addCut('_goodJets_1_Pt>60')
dc.addCut('_muAndMETMT>50')

dc.setData('trees/stpol_data_3J1T.root', 808.472)

dc.addMC('trees/stpol_ttbar_3J1T.root', 234, 'ttbar', drawfw.ROOT.kOrange+7)
dc.addMC('trees/stpol_wjets_3J1T.root', 36257.2, 'wjets', drawfw.ROOT.kGreen)

if len(sys.argv) > 1 and sys.argv[1] == 'test':
	print 'Entering test mode!'
	p=dc.plot('_recoTop_0_Mass', 50, 650, 16, 'topmass')
	drawfw.TCanvas()
	p.draw()
	p.legend.Draw('SAME')
	raw_input()
else:
	dc.plot('_recoTop_0_Mass', 50, 650, 16, 'topmass').save('plot_topmass_drawfw.png')
	dc.plot('_lowestBTagJet_0_Eta', -5, 5, 16, 'jeteta').save('plot_jeteta_drawfw.png')
	dc.plot('abs(_lowestBTagJet_0_Eta)', 0, 4.5, 16, 'abseta').save('plot_abseta_drawfw.png')
	dc.plot('_recoTop_0_Pt', 0, 500, 16, 'toppt').save('plot_jeteta_drawfw.png')
