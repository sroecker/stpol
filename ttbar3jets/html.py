import argparse, re, cPickle
from os import listdir
from os.path import isfile, join

# Argument parsing
parser = argparse.ArgumentParser(description='Creates plots of a dataset.')
parser.add_argument('-d', '--dir', default='plots')
parser.add_argument('-r', '--regexp', default='(.*)\.png')
parser.add_argument('-o', '--out', default='plots.html')

args = parser.parse_args() # with bad arguments the script stops here

# Params
ofile = args.dir+'/'+args.out
regexp = args.regexp
print 'Outputting to:', ofile
print 'Regular expression: `%s`'%regexp

fh=open(ofile, 'w')
fh.write('<html>' + "\n");
#fh.write('<head>' + "\n");
#fh.write('</head>' + "\n");
fh.write('<body>' + "\n");

files = listdir(args.dir)
rec = re.compile(regexp)
files.sort()
files = filter(rec.match, files)

print 'Files:'
for f in files:
	print '*', f
	fh.write('<hr />' + "\n")
	fh.write('<h1>%s</h1>'%f + "\n")
	fh.write('<img src="%s" />'%f + "\n")
	fh.write('<p>' + "\n")
	
	logfile = args.dir+'/'+''.join(f.split('.')[0:-1]) + '.pylog'
	#print 'Check logfile:', logfile
	if isfile(logfile):
		print '  Log:', logfile
		log_fh=open(logfile, 'r')
		log=cPickle.load(log_fh)
		log_fh.close()
		
		# Cuts
		fh.write('<b>Cut string:</b> %s'%log.cutstring + "\n")
		fh.write('<table border="1">' + "\n")
		fh.write('<tr><th>Cuts (&&-ed together):</th></tr>' + "\n")
		for c in log.cuts:
			fh.write('<tr><td>%s</td></tr>'%c + "\n")
		fh.write('</table>' + "\n")
		
		# Parameters
		fh.write('<table border="1">' + "\n")
		fh.write('<tr><th>Parameter</th><th>Value</th></tr>' + "\n")
		for p in log._params:
			fh.write('<tr><td>%s</td><td>%s</td></tr>'%(p['title'], p['value']) + "\n")
		fh.write('</table>' + "\n")
		
		# Table of data/mc stuff
		fh.write('<table border="1">' + "\n")
		data_pcs = [(k,v) for (k,v) in log._processes.items() if not v['ismc']]
		mc_pcs = [(k,v) for (k,v) in log._processes.items() if v['ismc']]
		
		fh.write('<tr>' + "\n")
		fh.write('<td class="label">Title:</td>' + "\n")
		for k,v in mc_pcs:
			fh.write('<td>%s</td>'%v['title'] + "\n")
		for k,v in data_pcs:
			fh.write('<td>%s</td>'%v['title'] + "\n")
		fh.write('</tr>' + "\n")
		
		for var in log._variables.keys():
			fh.write('<tr>' + "\n")
			fh.write('<td class="label">%s:</td>'%log._variables[var]['title'] + "\n")
			for mck,mcv in mc_pcs:
				if var in mcv['vars']:
					fh.write('<td>%s</td>'%str(mcv['vars'][var]) + "\n")
				else:
					fh.write('<td>-</td>' + "\n")
			for dtk,dtv in data_pcs:
				if var in dtv['vars']:
					fh.write('<td>%s</td>'%str(dtv['vars'][var]) + "\n")
				else:
					fh.write('<td>-</td>' + "\n")
			fh.write('</tr>' + "\n")
		
		fh.write('</table>' + "\n")
	else:
		fh.write('Logfile not present!' + "\n")
	
	
	fh.write('</p>' + "\n")

fh.write('</body>' + "\n");
fh.write('</html>' + "\n");

fh.close()
