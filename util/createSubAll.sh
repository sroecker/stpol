#!/bin/bash

for f in *.cfg
do
	crab -cfg $f -create
done

for f in WD*
do
	crab -c $f -submit
done
