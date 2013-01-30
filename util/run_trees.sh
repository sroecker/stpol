#!/bin/bash

JOBNUM=$1

. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/T_t.txt trees/T_t $JOBNUM "channel=signal subChannel=T_t"
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/Tbar_t.txt trees/Tbar_t channel=signal subChannel=Tbar_t
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/T_tW.txt trees/T_tW channel=background subChannel=T_tW
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/Tbar_tW.txt trees/Tbar_tW channel=background subChannel=Tbar_tW
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/T_s.txt trees/T_s channel=background subChannel=T_s
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/Tbar_s.txt trees/Tbar_s channel=background subChannel=Tbar_s
. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/TTbar.txt trees/TTbar $JOBNUM "channel=background subChannel=TTbar"
. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/WJets.txt trees/WJets $JOBNUM "channel=background subChannel=WJets"
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/WW.txt trees/WW channel=background subChannel=WW
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/WZ.txt trees/WZ channel=background subChannel=WZ
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/ZZ.txt trees/ZZ channel=background subChannel=ZZ
#. ./util/bcmsRun runconfs/step2_newCmdLine_cfg.py fileLists/SingleMu1.txt trees/SingleMu isMC=False
