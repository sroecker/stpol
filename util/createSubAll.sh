#!/bin/bash

for f in *.cfg
do
	crab -cfg $f -create
done

for f in WD_*
do
    for i in {1..3}
    do
        crab -c $f -submit 500
        if [ $? -ne 0 ]; then break; fi
    done
done
