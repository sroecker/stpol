import json
import sys

d = json.load(open(sys.argv[1]))
runs = map(lambda x: x.strip(), open(sys.argv[2]).readlines())
newD = dict()
for r in runs:
    newD[r] = d[r]
print json.dumps(newD)
