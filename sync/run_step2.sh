#!/bin/bash
cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py inputFiles=file:$STPOL_DIR/sync/inclusive/step1_noSkim.root channel=signal subChannel=T_t outputFile=$STPOL_DIR/sync/inclusive/step2.root
cmsRun $STPOL_DIR/runconfs/step2_newCmdLine_cfg.py inputFiles=file:$STPOL_DIR/sync/exclusive/step1_noSkim.root channel=signal subChannel=T_t outputFile=$STPOL_DIR/sync/exclusive/step2.root
