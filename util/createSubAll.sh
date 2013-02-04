#!/bin/bash

for f in *.cfg
do
	crab -cfg $f -create
    while true
    do
	    crab -c $f -submit 500
        if [ $? -ne 0 ]; then break; fi
    done
done
