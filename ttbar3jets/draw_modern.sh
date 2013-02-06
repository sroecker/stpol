#!/bin/bash
file_path="/home/joosep/singletop/data/trees/Feb5_A/Iso/"
file_mc=${file_path}"TTbar.root"
file_dt=${file_path}"SingleMu.root"
echo ${file_mc} ${file_dt}

script="draw_single.py"
cuts="--cut _goodJets_0_Pt>60 --cut _goodJets_1_Pt>60 --cut _muAndMETMT>50"
flags="--info"
fname="cuts_met"

echo ">>> Plotting: Light Jet Eta <<<"
python $script $flags "_lowestBTagJet_0_Eta" $file_mc $file_dt --hist -5 5 $cuts -b --save plot_jeteta_${fname}.png
echo

echo ">>> Plotting: Abs of Light Jet Eta <<<"
python $script $flags "abs(_lowestBTagJet_0_Eta)" $file_mc $file_dt --hist 0 4.5 $cuts -b --save plot_abseta_${fname}.png
echo

echo ">>> Plotting: Top mass <<<"
python $script $flags _recoTop_0_Mass $file_mc $file_dt --hist 50 650 $cuts -b --save plot_topmass_${fname}.png
echo

echo ">>> Plotting: Top Pt <<<"
python $script $flags _recoTop_0_Pt $file_mc $file_dt --hist 0 500 $cuts -b --save plot_toppt_${fname}.png
