import tables
import sys

fi = tables.openFile(sys.argv[1], "r", "Test")
of = tables.openFile("out.h5", "w", "Out")
import pdb

nodes = []
allcols = dict()
for node in fi:
    if hasattr(node, "name") and node.name == "eventTree":
        print node.name
        for coln in node.colnames:
            allcols[coln] = node.coldescrs[coln]
        nodes.append(node._v_pathname)
pdb.set_trace()
nRows = fi.getNode(nodes[0]).nrows
newT = of.createTable("/", "newT", allcols, expectedrows=nRows, filters=tables.Filters(complevel=9, complib='blosc', fletcher32=False))
row = newT.row
for i in range(nRows):
    row.append()
newT.flush()
print len(nodes)
for nodeName in nodes:
    node = fi.getNode(nodeName)
    for coln in node.colnames:
        print "putting {0}".format(coln)
        newT.modifyColumn(colname=coln, column=node.colinstances[coln][:])
    newT.flush()

