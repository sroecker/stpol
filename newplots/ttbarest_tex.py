import cPickle

# Params
files = [
	('3J1T', 'costheta', '$\\cos(\\theta)$'),
	('3J1T', 'topmass', 'Top mass'),
	('3J1T', 'toppt', 'Top $p_t$'),
	('3J1T', 'bjeteta', '$\\eta$ of lowest b-tag jet'),
	('3J2T', 'costheta', '$\\cos(\\theta)$'),
	('3J2T', 'topmass', 'Top mass'),
	('3J2T', 'toppt', 'Top $p_t$'),
	('3J2T', 'bjeteta', '$\\eta$ of lowest b-tag jet')
]

for f in files:
	logfile = 'plots_ttbar/ttbar_%s_%s.pylog'%(f[0],f[1])
	#print 'logfile:',logfile
	
	log_fh=open(logfile, 'r')
	log=cPickle.load(log_fh)
	log_fh.close()
	
	kg = log._params['Kolmogorov test']
	#print '%.5f'%kg
	print '\\plot{%s}{%s}{%s}{%.5f}'%(f[0],f[1],f[2],kg)
