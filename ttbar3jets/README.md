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


Drawing the graphs
------------------
`draw.py` can be used to draw the graphs.

For example, to draw the graph of the top mass:
> `python draw.py --hist 0 800 --bins 20 treesCands _recoTop_0_Mass mc_file.root data_file.root`

Parameters of the `draw.py` script:

	usage: draw.py [-h] [--hist min max] [--bins BINS] [--save SAVE] [-b]
				   tree var mc data

	Plots MC and Data for some variable.

	positional arguments:
	  tree
	  var
	  mc
	  data

	optional arguments:
	  -h, --help      show this help message and exit
	  --hist min max  min and max boundary values for the histogram
	  --bins BINS     number of histogram bins
	  --save SAVE     save the histogram to a file
	  -b              run in batch mode. Requires --save.

### Note on the PyROOT argument parsing ###
PyROOT also parses command line arguments.

If `-b` is present, X windows etc. are not created.
In addition to that, `draw.py` also uses that flag to slightly change
the way it executes.

Similarly, the `-h` gives the PyROOT help, not the help generated
by `argparse`.



Information about ROOT files
----------------------------
`working.py` gives a quick overview of some of the parameters of
a particular ROOT file.
