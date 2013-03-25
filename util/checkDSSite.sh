#!/bin/bash
while read line
do
    echo $line" | "`python ~/util/das_cli.py --query="file dataset=$line" --limit=0 | grep T2_EE_Estonia`
done
