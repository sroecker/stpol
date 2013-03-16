echo "Setting up stpol env..."

# Extract directories
CURRENT_DIR=`pwd`
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#echo "Current:" $CURRENT_DIR
#echo "Script:" $SCRIPT_DIR

export local_dbs_instance=cms_dbs_ph_analysis_02
export local_dbs_url=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd ${SCRIPT_DIR}/CMSSW_5_3_7_patch4
#cmsenv
eval `scramv1 runtime -sh`

cd $CURRENT_DIR
