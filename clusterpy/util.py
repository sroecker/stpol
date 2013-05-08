def cluster_setup():
    from IPython.parallel import Client
    import IPython.parallel
    try:
        c = Client("/home/joosep/.ipython/profile_default/security/ipcontroller-client.json")
        dview = c[:]
        print "Got %d engines" % len(c.ids)
        return dview
    except Exception as e:
        print "No engines were available: %s" % str(e)

from IPython.core.display import Image
def to_png(filename):
    get_ipython().system('gs -q -dNOPAUSE -dBATCH -sDEVICE=pngalpha -dEPSCrop -sOutputFile="$filename".png "$filename".pdf')

def show_canv(canv):
    canv.SaveAs("test.pdf")
    to_png("test")
    return Image(filename='test.png')

def hostnames():
    import socket
    import os
    return socket.gethostname() + ":" + str(os.getpid())

def has_root():
    try:
        import ROOT
        return "ROOT:" + str(ROOT.gROOT.GetVersion())
    except Exception as e:
        raise e
