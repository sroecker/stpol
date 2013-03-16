import cPickle

# Params
files = [
	('3J1T', 'costheta', '$\\cos(\\theta)$'),
	('3J1T', 'topmass', 'Top mass'),
	#('3J1T', 'toppt', 'Top $p_t$'),
	('3J1T', 'bjeteta', 'light jet $\\eta$'),
	('3J2T', 'costheta', '$\\cos(\\theta)$'),
	('3J2T', 'topmass', 'Top mass'),
	#('3J2T', 'toppt', 'Top $p_t$'),
	('3J2T', 'bjeteta', 'light jet $\\eta$'),

	('3J1T', 'costheta_b', '$\\cos(\\theta)$ (w b-weight)'),
	('3J1T', 'topmass_b', 'Top mass (w b-weight)'),
	('3J1T', 'bjeteta_b', 'light jet $\\eta$ (w b-weight)'),
	('3J2T', 'costheta_b', '$\\cos(\\theta)$ (w b-weight)'),
	('3J2T', 'topmass_b', 'Top mass (w b-weight)'),
	('3J2T', 'bjeteta_b', 'light jet $\\eta$ (w b-weight)')
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
