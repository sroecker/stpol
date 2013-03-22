#!/usr/bin/python
import re
import sys

if len(sys.argv)==1:
    print "Usage: {0} prefix".format(sys.argv[0])
    sys.exit(1)

prefix=sys.argv[1]
lines = sys.stdin.readlines()
lines = map(lambda x: x.strip(), lines)

for v in lines:
    print prefix + v
