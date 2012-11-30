#/bin/bash
file_mc="stpol_TTbar_3J1T_numEvent2000000_trees.root"
file_dt="stpol_Data_3J1T_numEvent10000000_trees.root"

python draw.py _fwdMostLightJet_0_Eta $file_mc $file_dt --hist -6.28 6.28 -b --save plot_jeteta.png
python draw.py _recoTop_0_Mass $file_mc $file_dt --hist 0 800 -b --save plot_topmass.png
