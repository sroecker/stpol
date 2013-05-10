import argparse
import ROOT
import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")
from plotfw import drawfw
from plotfw.params import Cuts
import plotfw.methods
from plotfw.params import Cut
from plotfw.methods import PlotParams
from plotfw.params import Cut, Vars
import pdb
import samples
import os
import random
import string
import pickle
import multiprocessing

parser = argparse.ArgumentParser()
parser.add_argument('-o', '--ofdir', type=str, default="plots_out_" + ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(4)))
parser.add_argument('-p', '--percent', type=float, default=100.0)
parser.add_argument('-i', '--mc_dir', type=str, default="/scratch/joosep/step2_MC_Iso_Mar14/")
parser.add_argument('-n', '--n_cores', type=int, default=8)
args = parser.parse_args()

samples = dict()
samples["TTJets_FullLept"] = plotfw.methods.MCSample("WD_TTJets_FullLept", name="TTJets_FullLept", directory=args.mc_dir)
samples["TTJets_SemiLept"] = plotfw.methods.MCSample("WD_TTJets_SemiLept", name="TTJets_SemiLept", directory=args.mc_dir)
samples["TTJets_inclusive"] = plotfw.methods.MCSample("WD_TTJets_MassiveBinDECAY", name="TTbar", directory=args.mc_dir)
samples["T_t"] = plotfw.methods.MCSample("WD_T_t", name="T_t", directory=args.mc_dir)
samples["W1Jets"] = plotfw.methods.MCSample("WD_W1Jets_exclusive", name="W1Jets", directory=args.mc_dir)
samples["W2Jets"] = plotfw.methods.MCSample("WD_W2Jets_exclusive", name="W2Jets", directory=args.mc_dir)
samps = samples.values()
groups = plotfw.methods.SampleGroup.fromList(samples.values())
sl = plotfw.methods.SampleList()
sl.addGroups(groups)

#pp1 = PlotParams(Vars.cos_theta, [-1, 1])
#pp2 = PlotParams(Vars.met, [0, 200])
#
#hists = sl.drawHists("cos_theta", pp1, Cuts.finalMu_2J0T, 0.1, n_cores=8)
#for hn, h in hists:
#    print hn + ":" + str(h)
#hists = sl.drawHists("met", pp2, Cuts.finalMu_2J0T, 0.1, n_cores=8)
#for hn, h in hists:
#    print hn + ":" + str(h)

comp_samples = plotfw.drawfw.ShapePlotCreator(sl)
comp_samples.set_n_cores(8)
comp_samples.frac_entries = 0.05
psMu = []
psMu += comp_samples.plot(Cuts.finalMu_2J1T, [PlotParams(Vars.cos_theta, [-1, 1], normalize_to="unity")], cutDescription="muon channel, final sel. (2J0T)")
psMu[0].save(ofdir=".", fmt="pdf", log=False)
