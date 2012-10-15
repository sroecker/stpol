# Usage: python2.7 pathDumper.py my_cfg myPath
# my_cfg.py must exist in the cwd

import sys
import os
sys.path.append(os.getcwd())
import importlib
fname = sys.argv[1]
ipath = sys.argv[2]

sys.argv = sys.argv[3:]
sys.argv.insert(0, fname + ".py")
mod = importlib.import_module(fname)
process = mod.process

path = getattr(process, ipath)
s = map(lambda x: str(x) + " = " + repr(x), [getattr(process, x) for x in str(path).split("+")])
of = open(path.label() + "_dump.txt", "w")
of.writelines(s)
of.close()
