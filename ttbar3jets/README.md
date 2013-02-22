TTBar estimation
================
The goal is to select a ttbar enriched region and compare
the distribution of some interesting variable to data.


Generating ROOT files
---------------------
ROOT TTrees are created using `/runconfs/step2_cfg.py` script.

Example:
> `cmsRun ../runconfs/step2_cfg.py inputFiles_load=../fileLists/TTBar.txt maxEvents=25000 outputFile=stpol_TTBar_3J1T.root nJ=3 nB=1 mc hlt mu >3J1T_25k.log 2>&1`

The file lists used:

*	For MC: `/fileLists/TTBar.txt`
*	For data: `/fileLists/SingleMu1.txt`

`util/bcmsRun` (parallelised version of `cmsRun`) can be used to create
TTrees more quickly.

Example:
> `. ../../util/bcmsRun ../../runconfs/step2_cfg.py ../../fileLists/TTBar.txt ttbar nJ=3 nB=1 mc hlt mu`

Drawing the graphs
------------------
`draw_single.py` can be used to draw the graphs.

For example, to draw the graph of the top mass:
> `python draw_single.py --hist 0 800 --bins 20 _recoTop_0_Mass mc_file.root data_file.root`

Parameters of the `draw_single.py` script:

	usage: draw_single.py [-h] [-c CUT] [--hist min max] [--bins BINS] [-i]
						  [--save SAVE] [-b]
						  var mc data

	Plots MC and Data for some variable.

	positional arguments:
	  var
	  mc
	  data

	optional arguments:
	  -h, --help         show this help message and exit
	  -c CUT, --cut CUT  additional cuts
	  --hist min max     min and max boundary values for the histogram
	  --bins BINS        number of histogram bins
	  -i, --info         create another pad with important values and variables
	  --save SAVE        save the histogram to a file
	  -b                 run in batch mode. Requires --save.

### Note on the PyROOT argument parsing ###
PyROOT also parses command line arguments.

If `-b` is present, X windows etc. are not created.
In addition to that, `draw_single.py` also uses that flag to slightly change
the way it executes.

Similarly, the `-h` gives the PyROOT help, not the help generated
by `argparse`.



Information about ROOT files
----------------------------
`working.py` gives a quick overview of some of the parameters of
a particular ROOT file.


Structure of step2 root files
-----------------------------
All jets are stored in the decreasing order of Pt as
`_goodJets_n_*`, where `n=0,1,2,...`.

Light jet is `_lowestBTagJet_0_*` (previously `_fwdMostLightJet_0_`)
