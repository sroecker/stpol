import autoLoad
import logging
logging.basicConfig(level=logging.WARNING, format="%(asctime)s;%(levelname)s;%(name)s;%(message)s")
import plotfw.methods
import plotfw.drawfw
import plotfw.params
import ROOT
import argparse
from plotfw.params import Cuts
from plotfw.params import Vars
import random
import string
import numpy
import unittest


mc_dir = "/home/joosep/singletop/stpol/crabs/step2_MC_Iso_Mar14/"
data_dir = "/home/joosep/singletop/stpol/crabs/step2_Data_Iso_Mar15/"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
class SampleTestBase(unittest.TestCase):
    max_lines = 25000.0
    def loadMCSample(self, sample_name, indir):
        return plotfw.methods.MCSample("WD_%s" % (sample_name), name=sample_name, directory=indir)

    def loadDataSample(self, sample_name, indir):
        return plotfw.methods.DataSample("WD_%s" % (sample_name), 1, name=sample_name, directory=indir)

    def base_test_sample_costheta(self, sample):
        cos_vals = sample.getColumn(Vars.cos_theta, Cuts.finalMu_2J1T, maxLines=self.max_lines)
        assert(len(cos_vals)>0)
        logger.info("sample %s 2J1T cut eff = %.2E" % (sample, float(len(cos_vals))/self.max_lines))
        assert(numpy.mean(cos_vals) > -1)
        assert(numpy.all(numpy.abs(cos_vals) < 1) == True)

    def base_test_sample_b_weights(self, sample):
        vals = sample.getColumn(Vars.b_weight["nominal"], Cuts.finalMu_2J1T, maxLines=self.max_lines)
        mean_weight = numpy.mean(vals)
        logger.info("sample %s mean b_weight[nominal] = %.2f" % (sample, mean_weight))
        assert(len(vals)>0)
        assert(mean_weight > 0)

    def base_test_sample_pu_weight(self, sample):
        vals = sample.getColumn(Vars.pu_weight, Cuts.finalMu_2J1T, maxLines=self.max_lines)
        mean_weight = numpy.mean(vals)
        logger.info("sample %s mean PU weight = %.2f" % (sample, mean_weight))
        assert(len(vals)>0)
        assert(mean_weight > 0)

    def test_T_t(self):
        sample = self.loadMCSample("T_t", mc_dir)
        self.base_test_sample_costheta(sample)
        self.base_test_sample_b_weights(sample)
        self.base_test_sample_pu_weight(sample)

    def test_TTJets_FullLept(self):
        sample = self.loadMCSample("TTJets_FullLept", mc_dir)
        self.base_test_sample_costheta(sample)
        self.base_test_sample_b_weights(sample)
        self.base_test_sample_pu_weight(sample)

    def test_SingleMuD(self):
        sample = self.loadDataSample("SingleMuD", data_dir)
        self.base_test_sample_costheta(sample)

if __name__=="__main__":
    unittest.main()
