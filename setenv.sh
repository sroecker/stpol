echo "Setting up stpol env..."

# Extract directories
CURRENT_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CMSSW_DIR=$1
if [ -z "$CMSSW_DIR" ]; then CMSSW_DIR="CMSSW_5_3_7_patch4"; fi
#echo "Current:" $CURRENT_DIR
#echo "Script:" $SCRIPT_DIR

# Set up CMSSW env
export STPOL_DIR=$SCRIPT_DIR
export local_dbs_instance=cms_dbs_ph_analysis_02
export local_dbs_url=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ${SCRIPT_DIR}/$CMSSW_DIR
#cmsenv
eval `scramv1 runtime -sh`

# Add plotfw to python library path
#PYTHONPATH=$PYTHONPATH:${SCRIPT_DIR}/newplots
PYTHONPATH=$PYTHONPATH:`readlink -f runconfs`:$SCRIPT_DIR/plots

# Return to original directory
cd $CURRENT_DIR
