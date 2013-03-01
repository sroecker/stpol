#!/usr/bin/python
import re
import sys
import math

lines = open(sys.argv[1]).readlines()
pat = re.compile(".+,.+,.+,.+,([0-9]*\.[0-9]+)")

lumi = 0
for line in lines:
    match = pat.match(line)
    if not match is None:
        lumi += float(match.group(1))
print int(round(lumi/1000000))
