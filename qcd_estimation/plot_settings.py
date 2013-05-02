from ROOT import *

gStyle.Reset()

gStyle.SetFrameBorderMode(0)
gStyle.SetCanvasBorderMode(0)
#  gStyle.SetOptStat(0)
gStyle.SetPadColor(0)
gStyle.SetCanvasColor(0)
gStyle.SetStatColor(0)
gStyle.SetLegendBorderSize(0)

gStyle.SetLabelColor(1, "XYZ")
gStyle.SetLabelFont(42, "XYZ")
gStyle.SetLabelOffset(0.007, "XYZ")
gStyle.SetLabelSize(0.05, "XYZ")


# For the axis:                                                                                                                                             

gStyle.SetAxisColor(1, "XYZ")
#gStyle.SetStripDecimals(kTRUE)

gStyle.SetTickLength(0.03, "XYZ")
gStyle.SetNdivisions(510, "XYZ")
gStyle.SetPadTickX(1)  #// To get tick marks on the opposite side of the frame                                                                          
gStyle.SetPadTickY(1)

#// Change for log plots:                                                                                                                                     
gStyle.SetOptLogx(0)
gStyle.SetOptLogy(0)
gStyle.SetOptLogz(0)

#// Postscript options:                                                                                                                                       
gStyle.SetPaperSize(20.,20.)

