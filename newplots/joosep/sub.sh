sbatch -c 5 runOnCluster.sh -n 5 -p 100 --useHDFS --doFinalSel --doReweight
sbatch -c 5 runOnCluster.sh -n 5 -p 100 --useHDFS --doMET --doReweight
sbatch -c 5 runOnCluster.sh -n 5 -p 100 --useHDFS --doNJets --doReweight
sbatch -c 5 runOnCluster.sh -n 5 -p 100 --useHDFS --doNBTags --doReweight
sbatch -c 5 runOnCluster.sh -n 5 -p 100 --useHDFS --doTopMass --doReweight
