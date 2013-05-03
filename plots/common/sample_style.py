from colors import sample_colors_same as sample_colors
import ROOT

class Styling:
    @staticmethod
    def mc_style(hist, sample_name):
        color = sample_colors[sample_name]
        hist.SetLineColor(color)
        hist.SetLineWidth(2)
        hist.SetFillColor(color)
        hist.SetFillStyle(1001)
    
    
    @staticmethod
    def data_style(hist):
        hist.SetMarkerStyle(20)
        hist.SetMarkerColor(ROOT.kBlack)
        hist.SetFillStyle(4001)