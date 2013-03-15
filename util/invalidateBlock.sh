#!/bin/bash
python ~/util/das_cli.py --query="file block=$1 instance=cms_dbs_ph_analysis_02" --limit=0 > inv.txt
while read p
do
    python ~/singletop/stpol/util/dbsInvalidateFile.py --DBSURL=https://cmsdbsprod.cern.ch:8443/cms_dbs_ph_analysis_02_writer/servlet/DBSServlet --lfn=$p
done < inv.txt
