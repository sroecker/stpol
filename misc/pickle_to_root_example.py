import ROOT
import pickle
from datetime import datetime

tfile = ROOT.TFile('asdf.root', 'READ')
if tfile.IsOpen():
	print 'Reading from tfile...'
	subdir = tfile.GetDirectory('sub')
	obj = ROOT.TObjString()
	subdir.ReadTObject(obj, 'rnd_arr')
	print pickle.loads(obj.String().Data())
else:
	print 'No tfile!'

print '(Re)creating the tfile'
tfile = ROOT.TFile('asdf.root', 'RECREATE')
subdir = tfile.mkdir('sub')

un_dict = {
	'int': 123,
	'string': 'asdasdasd',
	'float': 46.901930123,
	'list': [1,2,3,4],
	'today': datetime.today()
}

arr = ROOT.TObjString(pickle.dumps(un_dict))
subdir.WriteTObject(arr, 'rnd_arr')
