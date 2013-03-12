Utilities
=========

bcmsRun
-------

Parallelises the cmsRun command if the input is a list of files.
It splits the file list into equal chunks and creates the TTrees in
parallel.

	usage: . bcmsRun config filelist jobname [cmsRun, ...]
	
	Parallelised version of the cmsRun. Note that an initialized
	CMSSW environment is required (hence the ".").
	
	Arguments:
	  config    configuration file
	  filelist  list of root files
	  jobname   job identifier
	  cmsRun    optional arguments that are passed directly to cmsRun

The script will create a directory called `jobname`. The directory must
not exists. Job, log and root files are all placed in that directory.
A new root file is created for each chunck. After the `cmsRun` commands
completes, `hadd` can be used to add all the root files together.

Example:
> `hadd outfile.root jobname/*.root`
