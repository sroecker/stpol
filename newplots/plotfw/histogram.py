import ROOT
import logging

class Histogram(ROOT.TH1F):
	def __init__(self, *args):
		super(Histogram, self).__init__(*args)
		self.Sumw2()
		self.SetStats(False)
		self.err = None
		self.integral = None
		self.child_hists = []
		self.count_events = self.GetEntries()
		self.is_normalized = False

	def calc_int_err(self):
		err = ROOT.Double()
		integral = self.IntegralAndError(1, self.GetNbinsX(), err)
		self.err = err
		self.integral = integral

	def get_err(self):
		if self.err is None:
			self.calc_int_err()
		return self.err

	def get_integral(self):
		if self.integral is None:
			self.calc_int_err()
		return self.integral
	def normalize(self):
		if self.Integral()>0:
			self.Scale(1.0/self.Integral())
			self.is_normalized = True
		else:
			logging.warning("Histogram integral=0, not scaling")

	def Add(self, other):
		o = other.Clone()
		super(Histogram, self).Add(o)
		self.child_hists.append(other)

	def __str__(self):
		return "Histogram(%s) with %d bins, mean=%.2f, int=%.2f, err=%.2f" % (self.GetName(), self.GetNbinsX(), self.GetMean(), self.get_integral(), self.get_err())

if __name__=="__main__":
	import unittest
	class TestHistogram(unittest.TestCase):
		def test_histo_create(self):
			h = Histogram("my_hist", "My Hist", 10, -1, 1)
			assert(h.GetName() == "my_hist")
			assert(h.GetTitle() == "My Hist")

		def test_histo_clone(self):
			h1 = Histogram("my_hist", "My Hist", 10, -1, 1)
			h2 = Histogram(h1)
			assert(h1.GetName() == h2.GetName())

		def test_histo_fill(self):
			import random
			h = Histogram("my_hist", "My Hist", 10, -1, 1)
			for i in range(1000):
				h.Fill(random.random())
			m = h.GetMean()
			assert(m>0 and m<1)

		def test_histo_err_int(self):
			import random
			h = Histogram("my_hist", "My Hist", 10, -1, 1)
			for i in range(1000):
				h.Fill(random.random())
			err = h.get_err()
			integral = h.get_integral()
			assert(err>0)
			assert(integral>0)

	unittest.main()

