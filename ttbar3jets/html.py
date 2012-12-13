import argparse, re
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
print 'Outputting to:', ofile
print 'Regular expression: `%s`'%args.regexp

fh=open(ofile, 'w')
fh.write('<html>' + "\n");
#fh.write('<head>' + "\n");
#fh.write('</head>' + "\n");
fh.write('<body>' + "\n");

files = listdir(args.dir)
rec = re.compile(args.regexp)
files.sort()
files = filter(rec.match, files)

print 'Files:'
for f in files:
	print '*', f
	fh.write('<p>' + "\n")
	fh.write('<h1>%s</h1>'%f + "\n")
	fh.write('<img src="%s" />'%f + "\n")
	fh.write('</p>' + "\n")

fh.write('</body>' + "\n");
fh.write('</html>' + "\n");
