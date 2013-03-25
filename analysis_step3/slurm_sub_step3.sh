#!/bin/bash
#This script will submit step2->step3 jobs to slurm
#INFILE is the absolute path to a file containing the input files, one per line, prepended with "file:"
#OUTDIR is the absolute path for the output directory, which must not exist but must be creatable with "mkdir"

INFILE=`readlink -f $1`
OUTDIR=`readlink -f $2`
if [ -z "$INFILE" ]; then
    echo "$0 INFILE JOBNAME"
    exit 1
fi
if [ -z "$OUTDIR" ]; then
    echo "$0 INFILE OUTDIR"
    exit 1
fi
#WD=$CMSSW_BASE/..
#rm -Rf $WD/$JOBNAME
mkdir $OUTDIR
cd $OUTDIR

#split input file into 30-line pieces
split $INFILE -l 50 -d
for file in x*
do
    sbatch $CMSSW_BASE/../analysis_step3/run_step3_eventloop.sh `readlink -f $file` $OUTDIR
done
