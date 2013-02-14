def th_sep(i, sep=','):
	i = abs(int(i))
	if i == 0:
		return '0'
	o = []
	while i > 0:
		o.append(i%1000)
		i /= 1000
	o.reverse()
	return str(sep).join([str(o[0])] + map(lambda x: '%03d'%x, o[1:]))

# Class to handle (concatenate) cuts
class Cut:
	def __init__(self, cutName, cutStr):
		self.cutName = cutName
		self.cutStr = cutStr
		#self.cutSequence = [copy.deepcopy(self)]

	def __mul__(self, other):
		cutName = self.cutName + " & " + other.cutName
		cutStr = '('+self.cutStr+') && ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __add__(self, other):
		cutName = self.cutName + " | " + other.cutName
		cutStr = '('+self.cutStr+') || ('+other.cutStr+')'
		newCut = Cut(cutName, cutStr)
		#newCut.cutSequence = self.cutSequence + other.cutSequence
		return newCut

	def __str__(self):
		return self.cutName + ":" + self.cutStr

	def __repr__(self):
		return self.cutName

# Single sample with a specified cross section
class Sample:
	def __init__(self, fname, xs, name=None):
		self.fname = fname
		self.xs = xs
		self.name = name

# Group of samples with the same color and label
class SampleGroup:
	def __init__(self, name, color):
		self.name = name
		self.color = color
		
		self.samples = [] # initially there are no samples
	
	def add(self, s):
		self.samples.append(s)
	
	def getName(self):
		return self.name
	
	def getLabel(self):
		return self.name
		
	def getColor(self):
		return self.color

class SampleList:
	def __init__(self, directory=''):
		self.directory = directory
		
		self.groups = {} # initially there are no sample groups
	
	def addGroup(self, g):
		self.groups[g.getName()] = g
	
	#def addSample(self, gn, s):
	#	self.groups[gn].add(s)
