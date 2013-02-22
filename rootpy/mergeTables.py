import tables
import sys
import pdb
import time
from collections import OrderedDict
from numpy.lib.recfunctions import merge_arrays
import math
import numpy

print "Running merge script"
infile = sys.argv[1]
outfile = infile.replace(".h5", "_opt.h5")

fi = tables.openFile(infile)
of = tables.openFile(outfile, "w", "SingleTopPolarization")

nodes = []
allcols = dict()
for node in fi:
    if hasattr(node, "name") and node.name == "eventTree":
        print node.name
        for coln in node.colnames:
            allcols[coln] = node.coldescrs[coln]
        nodes.append(node._v_pathname)


nodesToCreate = OrderedDict()

for key in allcols.keys():
    if allcols[key].dtype == "float64":
        nodesToCreate[key] = tables.Float32Col()
    elif allcols[key].dtype == "int64":
        nodesToCreate[key] = tables.Int32Col()
    else:
        nodesToCreate[key] = allcols[key]

nRows = fi.getNode(nodes[0]).nrows
#row = newT.row
#for i in range(nRows):
blocksize = 10000
nBlocks = int(math.ceil(nRows/blocksize))
print nBlocks
arrs = []
for nodeName in nodes:
    node = fi.getNode(nodeName)
    arrs.append(node[0])
merged = merge_arrays((arrs), asrecarray=True, flatten=True)
newT = of.createTable("/", "events", merged, expectedrows=nRows, filters=tables.Filters(complevel=0, complib='zlib', fletcher32=False))
for i in range(nBlocks):
    arrs = []
    for nodeName in nodes:
        node = fi.getNode(nodeName)
        arrs.append(node[i*blocksize:(i+1)*blocksize])
    [newT.append(numpy.empty((1, ), dtype=newT.dtype)) for j in range(blocksize)]
    for arr in arrs:
        newT.modifyColumns(i*blocksize, (i+1)*blocksize, columns=arr, names=arr.dtype.fields.keys())
    ndots = 100*i/nBlocks
    sys.stdout.write("\r" + "[" + "."*ndots + " "*(100-ndots) + "]")
    sys.stdout.flush()
    newT.flush()

print "Put {0} of {1} rows".format(newT.nrows, nRows)
#for nodeName in nodes:
#    node = fi.getNode(nodeName)
#
#    for coln in node.colnames:
#        t0 = time.time()
#        print "putting {0}".format(coln)
#        pdb.set_trace()
#        newT.modifyColumn(colname=coln, column=node.colinstances[coln][:])
#        newT.flush()
#        t1 = time.time()
#        dt = t1-t0
#        print "Done putting {0} in {1:.2f} sec".format(coln, dt)
