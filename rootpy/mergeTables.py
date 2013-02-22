import tables
import sys
import pdb
import time
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


nodesToCreate = {}

for key in allcols.keys():
    if allcols[key].dtype == "float64":
        nodesToCreate[key] = tables.Float32Col()
    elif allcols[key].dtype == "int64":
        nodesToCreate[key] = tables.Int32Col()
    else:
        nodesToCreate[key] = allcols[key]

nRows = fi.getNode(nodes[0]).nrows
newT = of.createTable("/", "events", nodesToCreate, expectedrows=nRows, filters=tables.Filters(complevel=0, complib='zlib', fletcher32=False))
row = newT.row
for i in range(nRows):
    row.append()
newT.flush()
print len(nodes)
for nodeName in nodes:
    node = fi.getNode(nodeName)

    for coln in node.colnames:
        t0 = time.time()
        print "putting {0}".format(coln)
        newT.modifyColumn(colname=coln, column=node.colinstances[coln][:])
        newT.flush()
        t1 = time.time()
        dt = t1-t0
        print "Done putting {0} in {1:.2f} sec".format(coln, dt)
