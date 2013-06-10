#!/bin/bash

dir=$1

echo "total split files"
find $dir -name "x*" -type f | wc -l
echo "total slurm jobs started"
find $dir -name "*.out" -type f | wc -l
echo "total slurm jobs successfully finished"
find $dir -name "*.out" -type f -exec grep "processing speed" {} \; | wc -l
echo "total slurm jobs with error"
find $dir -name "*.out" -type f -exec grep -i "error" {} \; | wc -l
