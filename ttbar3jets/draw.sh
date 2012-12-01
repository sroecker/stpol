#/bin/bash
file_mc="stpol_TTbar_3J1T_numEvent2000000_trees.root"
file_dt="stpol_Data_3J1T_numEvent10000000_trees.root"

cuts="--cut _fwdMostLightJet_0_Pt>60 --cut _fwdMostLightJet_0_rms<0.025"

echo ">>> Plotting: Forward Most Light Jet Eta <<<"
python draw.py _fwdMostLightJet_0_Eta $file_mc $file_dt --hist -6.28 6.28 $cuts -b --save plot_jeteta_cuts.png
echo

echo ">>> Plotting: Top mass <<<"
python draw.py _recoTop_0_Mass $file_mc $file_dt --hist 50 650 $cuts -b --save plot_topmass_cuts.png
echo

echo ">>> Plotting: Top Pt <<<"
python draw.py _recoTop_0_Pt $file_mc $file_dt --hist 0 500 $cuts -b --save plot_toppt_cuts.png
