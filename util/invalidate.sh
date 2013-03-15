#!/bin/bash
while read line
do
    ~/singletop/stpol/util/dbsInvalidateFile.py --DBSURL=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet --lfn=$line
done
