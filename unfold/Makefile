CC=g++
CXXFLAGS= -Wall -O2 -g -I./tunfold  `root-config --cflags --libs`
LDFLAGS=-L./tunfold -Wl,-rpath=./tunfold -lunfold -lMinuit

all: unfold calc_asymmetry unfold_syst_data calc_asymmetry_syst_data pseudodata

unfold: unfold.cc binnings.h utils.hpp
unfold_syst_data: unfold_syst_data.cc binnings.h utils.hpp
unfold_scan_mva: unfold_scan_mva.cc unfold.hpp binnings.h utils.hpp

unfold_lincheck: unfold_lincheck.cc binnings.h utils.hpp

calc_asymmetry: calc_asymmetry.C binnings.h utils.hpp
calc_asymmetry_syst: calc_asymmetry_syst.C binnings.h utils.hpp

bkg_asymmetry: bkg_asymmetry.C binnings.h utils.hpp

makehistos: makehistos.C xsec.h binnings.h
makehistos2: makehistos2.C xsec.h binnings.h

findbinning: findbinning.C info.h binnings.h

efficiency: efficiency.C histo.hpp xsec.h info.h binnings.h

rebin: rebin.C binnings.h info.h xsec.h 

plotfit: plotfit.C binnings.h utils.hpp

pseudodata: pseudodata.C binnings.h utils.hpp

clean:
	rm unfold calc_asymmetry bkg_asymmetry makehistos findbinning efficiency rebin plotfit eigenvalues pseudodata
