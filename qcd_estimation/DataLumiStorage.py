class DataLumiStorage:
    def __init__(self, isoLumi, antiIsoLumi):
        self._lumis = {}
        self._lumis["iso"] = isoLumi
        self._lumis["antiiso"] = antiIsoLumi
    
    def setDataLumi(self, iso, syst, lumi):
        self._lumis[iso+syst] = lumi
    
    #return relevant lumi
    def getDataLumi(self, iso):
        return self._lumis[iso]
