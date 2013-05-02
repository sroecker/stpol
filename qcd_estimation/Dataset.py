class Dataset:
   def __init__(self, name, tree, file_name, xs = 0, MC=True, lepton_type="all", prescale=1):
      self._name=name
      self._file_name=file_name
      self._tree=tree
      self._MC=MC
      self._lepton_type = lepton_type
      self._xs = xs
      self._prescale = prescale
      self._files = {}

   def GetFillStyle(self):
      if MC:
         return 0   
   
   def getFileName(self):
      return self._file_name

   def getName(self):
      return self._name

   def getTree(self):
      return self._tree

   def getLeptonType(self):
      return self._lepton_type

   def isMC(self):
      return self._MC

   def scaleToData(self, dataLumi):
      expected_events = self._xs * dataLumi
      total_events = self.getOriginalEventCount()      
      scale_factor = float(expected_events)/float(total_events)      
      return scale_factor

   def preScale(self):
      return self._prescale

   def addFile(self, syst, iso, f):
      self._files[syst+iso] = f

   def getFile(self, syst, iso):
      #print self._name, syst, iso, self._files
      return self._files[syst+iso]

   def setOriginalEventCount(self, count):
      self._originalEvents = count

   def getOriginalEventCount(self):
      return self._originalEvents
