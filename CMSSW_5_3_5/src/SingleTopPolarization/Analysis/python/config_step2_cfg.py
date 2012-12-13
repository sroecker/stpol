class C(object):
    @classmethod
    def _toStr(cls):
        s = ""
        for k in dir(cls):
            if k[0].islower():
                s += "\n%s = %s" % (k, getattr(cls, k))
        # for c in cls.__bases__:
        #     if hasattr(c, "toStr"):
        #         s += c.toStr()
        return s

class Config(C):
    class Channel:
        signal = "signal"
        background = "background"

    channel = Channel.background
    doMuon = True
    doElectron = True
    filterHLT = True
    useXTrigger = False
    isMC = True
    doDebug = False
    skipPatTupleOutput = False
    onGrid = False

    class Jets(C):
        cutJets = False
        nJets = 2
        nBTags = 1
        ptCut = 40
        etaCut = 4.7

        class BTagDiscriminant:
            TCHP = "trackCountingHighPurBJetTags"
            CSV_MVA = "combinedSecondaryVertexMVABJetTags"
        class BTagWorkingPoint:
            TCHPT = "TCHPT"
            CSVT = "CSVT"
            CSVM = "CSVM"

            WP = {"TCHPT":3.41, "CSVT":0.898, "CSVM":0.679}

        bTagDiscriminant = BTagDiscriminant.TCHP
        bTagWorkingPoint = BTagWorkingPoint.TCHPT

        @classmethod
        def BTagWorkingPointVal(c):
            return c.BTagWorkingPoint.WP[c.bTagWorkingPoint]

    class Leptons(C):
        class WTransverseMassType:
            MtW = "MtW"
            MET = "MET"

        class RelativeIsolation:
            rhoCorrRelIso = "rhoCorrRelIso"
            deltaBetaCorrRelIso = "deltaBetaCorrRelIso"

        reverseIsoCut = False
        cutOnIso = True
        cutOnTransverseMass = False
        transverseMassType = "MtW"
        transverseMassCut = 40
        relIsoType = RelativeIsolation.rhoCorrRelIso

        relIsoCutRangeIsolatedRegion = [0.0, 0.2]
        relIsoCutRangeAntiIsolatedRegion = [0.2, 0.5]
        looseVetoRelIsoCut = 0.2


    class Muons(Leptons):
        relIsoCutRangeIsolatedRegion = [0.0, 0.12]
        relIsoCutRangeAntiIsolatedRegion = [0.3, 0.5]
        looseVetoRelIsoCut = 0.2

    class Electrons(Leptons):
        pt = "ecalDrivenMomentum.Pt()"
        mvaCut = 0.9
        cutOnMVA = True
        relIsoCutRangeIsolatedRegion = [0.0, 0.1]
        relIsoCutRangeAntiIsolatedRegion = [0.1, 0.5]
        looseVetoRelIsoCut = 0.3


    Electrons.relIsoType = Leptons.RelativeIsolation.rhoCorrRelIso
    Muons.relIsoType = Leptons.RelativeIsolation.deltaBetaCorrRelIso

    # @classmethod
    # def toStr(c):
    #     s = "channel = %s" % Config.channel
    #     s += "\n" + Config.Jets.toStr()
    #     return s
