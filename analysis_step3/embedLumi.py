import re
import sys
import pdb
import argparse
import glob
import os

if __name__=="__main__":
    lumi_d = dict()

    for line in sys.stdin.readlines():
        line = line.strip()

        pat = re.compile("\| WD_(.*) \| .* \|  \| ([0-9]*) \|  \|")
        match = pat.match(line)
        if match is not None:
            print match.group(1), match.group(2)
            lumi_d[match.group(1)] = int(match.group(2))

    wd = "."
    for ds, lumi in lumi_d.items():
        files = glob.glob(wd + "/" + ds + ".root")
        if len(files)!=1:
            continue
        fi = files[0]
        new_fn = ds + "_" + str(lumi) + "_pb.root"
        os.rename(fi, new_fn)
