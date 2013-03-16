#!/bin/bash
#Runs th plots.py job on the cluster with any command line arguments specified by the user

WORKDIR=/home/joosep/singletop/stpol
source ~/.bash_profile

cd $WORKDIR
source setenv.sh

cd newplots
python plots.py -o "plots_out_cluster_"$SLURM_JOB_ID "$@"
#python plots.py "$@"
