#!/bin/bash
for i in WD*
do
    crab -c $i -kill all
done
