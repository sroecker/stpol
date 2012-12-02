#/bin/bash
file_mc="trees/stpol_ttbar_3J1T.root"
file_dt="trees/stpol_data_3J1T.root"

cuts="--cut _goodJets_0_Pt>60 --cut _goodJets_1_Pt>60"
flags="--info"

echo ">>> Plotting: Light Jet Eta <<<"
python draw.py $flags "_lowestBTagJet_0_Eta" $file_mc $file_dt --hist -5 5 $cuts -b --save plot_jeteta_cuts.png
echo

echo ">>> Plotting: Abs of Light Jet Eta <<<"
python draw.py $flags "abs(_lowestBTagJet_0_Eta)" $file_mc $file_dt --hist 0 4.5 $cuts -b --save plot_jeteta_cuts.png
echo

echo ">>> Plotting: Top mass <<<"
python draw.py $flags _recoTop_0_Mass $file_mc $file_dt --hist 50 650 $cuts -b --save plot_topmass_cuts.png
echo

echo ">>> Plotting: Top Pt <<<"
python draw.py $flags _recoTop_0_Pt $file_mc $file_dt --hist 0 500 $cuts -b --save plot_toppt_cuts.png
