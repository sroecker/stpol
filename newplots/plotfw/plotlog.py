import cPickle, logging

class PlotLog:
	def __init__(self, verbose=True):
		self.cuts = None
		self.cutstring = None

		self._variables = {}
		self._processes = {}
		self._params = {}

		self._v = verbose

	def setCuts(self, cuts, cutstring):
		self.cuts = cuts
		self.cutstring = cutstring

		if self._v:
			logging.debug('Generated cutstring: "%s"', self.cutstring)

	def addProcess(self, name, title=None, ismc=True):
		if name in self._processes:
			logging.warning('Process `%s` already exists!', name)
		else:
			self._processes[name] = {
				'title': title if title is not None else name,
				'ismc': bool(ismc),
				'vars': {}
			}

	def addParam(self, title, value):
#		np = {
#			'title': title,
#			'value': value
#		}
#
#		self._params.append(np)
		self._params[title] = value
		if self._v:
			logging.debug('P `%s`: %s', title, value)

	def getParam(self, par):
		return self._params[par]

	def setVariable(self, proc, var, value):
		if proc not in self._processes:
			logging.warning('Warning: Process `%s` does not exists!', var)
			return

		if var not in self._variables:
			self.addVariable(var)

		if var in self._processes[proc]['vars']:
			logging.debug('Notice: Variable already has value! (%s::%s)', proc, var)

		self._processes[proc]['vars'][var] = value
		if self._v:
			logging.debug('%s::%s: %s', proc, var, value)

	def addVariable(self, var, title=None):
		if var in self._variables:
			logging.debug('Notice: Variable `%s` already exists!', var)
		else:
			self._variables[var] = {
				'title': title if title is not None else var
			}

	def save(self, fname):
		logging.debug('Pickling log to `%s`', fname)
		fh = open(fname, 'w')
		cPickle.dump(self, fh, 0)
		fh.close()
