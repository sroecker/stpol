import ROOT
from DataFormats.FWLite import Events, Handle

events = Events('/hdfs/local/joosep/stpol/step2_MC_Iso_04_01/WD_T_t/res/output_10_1_zTW.root')

nrElSrc = ("electronCount")
nrElHandle = Handle( 'int')

for event in events:
    event.getByLabel(nrElSrc, nrElHandle)
    print nrElHandle.isValid()
    try:
        nrEl = (nrElHandle.product())[0]
    except RuntimeError as e:
        print "exception: %s" % (str(e))
        nrEl = 0

    print "nr electrons = " + str(nrEl)














