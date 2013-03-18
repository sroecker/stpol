sbatch -N 5 runOnCluster.sh -n 5 -p 1 --doFinalSel --doReweight
sbatch -N 5 runOnCluster.sh -n 5 -p 1 --doMET --doReweight
sbatch -N 5 runOnCluster.sh -n 5 -p 1 --doNJets --doReweight
sbatch -N 5 runOnCluster.sh -n 5 -p 1 --doNBTags --doReweight
sbatch -N 5 runOnCluster.sh -n 5 -p 1 --doTopMass --doReweight
