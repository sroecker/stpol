#!/bin/bash

for i in WD_*
do
    hadd $i.root `find . -wholename './'$i'/res/*.root'`
    if [ "$?" -ne 0 ]; then break; echo "Error!"; fi
done
