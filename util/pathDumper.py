
import sys
import os
sys.path.append(os.getcwd())
import importlib
path = sys.argv[1]
sys.argv = sys.argv[2:]
sys.argv.insert(0, path + ".py")
mod = importlib.import_module(path)
process = mod.process

path = process.singleTopPathStep1Mu
s = map(lambda x: str(x) + "=" + repr(x), [getattr(process, x) for x in str(path).split("+")])
of = open(path.label() + "_dump.txt", "w")
of.writelines(s)
of.close()
