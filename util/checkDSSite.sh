#!/bin/bash
while read line
do
    echo $line" | "`python ~/util/das_cli.py --query="dataset dataset=$line/*START53*/AODSIM" --limit=0`
done
