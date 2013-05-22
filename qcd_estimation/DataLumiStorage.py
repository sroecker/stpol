class DataLumiStorage:
    def __init__(self, isoLumi, antiIsoLumi):
        self._lumis = {}
        self._lumis["isoNominal"] = isoLumi
        self._lumis["antiisoNominal"] = antiIsoLumi
    
    def setDataLumi(self, iso, syst, lumi):
        self._lumis[iso+syst] = lumi
    
    #return relevant lumi
    def getDataLumi(self, iso, syst):
        return self._lumis[iso+syst]
