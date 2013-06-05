class Dataset:
   def __init__(self, name, file_name, xs = 0, MC=True, prescale=1):
      self._name=name
      self._file_name=file_name
      self._MC=MC
      self._xs = xs
      self._prescale = prescale
      self._files = {}
      self._originalEvents = {}

   def GetFillStyle(self):
      if MC:
         return 0   
   
   def getFileName(self):
      return self._file_name

   def getName(self):
      return self._name

   def isMC(self):
      return self._MC

   def scaleToData(self, dataLumi, syst, iso):
      expected_events = self._xs * dataLumi
      total_events = self.getOriginalEventCount(iso, syst)      
      scale_factor = float(expected_events)/float(total_events)      
      #print "scale: ",self._name,self._file_name,self._xs, dataLumi, self.getOriginalEventCount(iso, syst), scale_factor
      return scale_factor

   def preScale(self):
      return self._prescale

   def addFile(self, syst, iso, f):
      self._files[syst+iso] = f

   def getFile(self, syst, iso):
      #print self._name, syst, iso, self._files, self.isMC
      if not self.isMC(): #for data we don't have systematics
        return self._files["Nominal"+iso]
      else:
        return self._files[syst+iso]

   def setOriginalEventCount(self, count, iso, syst):
      self._originalEvents[iso+syst] = count

   def getOriginalEventCount(self, iso, syst):
      return self._originalEvents[iso+syst] 
