import re
import sys
import pdb
pat = re.compile(".*_([0-9]+)_([0-9]+)_.root")
lines = open(sys.argv[1]).readlines()
lines.sort()

fileD = dict()
print len(lines)
for line in lines:
    mat = pat.match(line)
    jobN = mat.group(1)
    fileN = mat.group(2)
    fileD[jobN] = line

ofile = open(sys.argv[1] + ".deduped", "w+")
for v in sorted(fileD.values()):
    ofile.write(v)
ofile.close()
